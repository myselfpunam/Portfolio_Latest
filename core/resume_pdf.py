from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate
from pathlib import Path
import reportlab


def _safe(value):
    return escape(' '.join(str(value or '').split()))


def _paragraph(text, style):
    return Paragraph(_safe(text), style)


def build_resume_pdf(profile, skills, experiences, education):
    """Render the portfolio's current CV data in the user's supplied clean CV style."""
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=20 * mm, leftMargin=20 * mm,
        topMargin=23 * mm, bottomMargin=22 * mm,
        title=f"{profile.name} - CV" if profile else 'CV',
        author=profile.name if profile else 'Portfolio',
    )
    font_dir = Path(reportlab.__file__).parent / 'fonts'
    if 'PortfolioVera' not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont('PortfolioVera', str(font_dir / 'Vera.ttf')))
        pdfmetrics.registerFont(TTFont('PortfolioVera-Bold', str(font_dir / 'VeraBd.ttf')))
        pdfmetrics.registerFont(TTFont('PortfolioVera-Italic', str(font_dir / 'VeraIt.ttf')))
        pdfmetrics.registerFont(TTFont('PortfolioVera-BoldItalic', str(font_dir / 'VeraBI.ttf')))
        pdfmetrics.registerFontFamily('PortfolioVera', normal='PortfolioVera', bold='PortfolioVera-Bold', italic='PortfolioVera-Italic', boldItalic='PortfolioVera-BoldItalic')
    base = getSampleStyleSheet()
    name_style = ParagraphStyle('CVName', parent=base['Normal'], fontName='PortfolioVera-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#111111'), spaceAfter=5)
    contact_style = ParagraphStyle('CVContact', parent=base['Normal'], fontName='PortfolioVera', fontSize=9.3, leading=13, textColor=colors.HexColor('#222222'), spaceAfter=2.5)
    section_style = ParagraphStyle('CVSection', parent=base['Heading2'], fontName='PortfolioVera-Bold', fontSize=12.2, leading=16, textColor=colors.HexColor('#111111'), spaceBefore=12, spaceAfter=5, keepWithNext=True)
    role_style = ParagraphStyle('CVRole', parent=base['Normal'], fontName='PortfolioVera-Bold', fontSize=10.2, leading=13.5, textColor=colors.HexColor('#161616'), spaceBefore=5, spaceAfter=2.5, keepWithNext=True)
    body_style = ParagraphStyle('CVBody', parent=base['Normal'], fontName='PortfolioVera', fontSize=10, leading=14.2, textColor=colors.HexColor('#202020'), spaceAfter=4, alignment=TA_LEFT)
    small_style = ParagraphStyle('CVSmall', parent=body_style, fontSize=9.7, leading=13.3, spaceAfter=3)
    bullet_style = ParagraphStyle('CVBullet', parent=small_style, leftIndent=11, firstLineIndent=-11)

    def bullet(text):
        return Paragraph(f"• {_safe(text)}", bullet_style)

    story = []
    if profile:
        story.append(_paragraph(profile.name, name_style))
        contacts = []
        if profile.email:
            contacts.append(f"Email: {_safe(profile.email)}")
        if profile.phone:
            contacts.append(f"Phone: {_safe(profile.phone)}")
        if contacts:
            story.append(Paragraph(' | '.join(contacts), contact_style))
        links = []
        if profile.linkedin_url:
            links.append(f"LinkedIn: {_safe(profile.linkedin_url.removeprefix('https://').removeprefix('http://'))}")
        if profile.github_url:
            links.append(f"GitHub: {_safe(profile.github_url.removeprefix('https://').removeprefix('http://'))}")
        if links:
            story.append(Paragraph(' | '.join(links), contact_style))
        if profile.website_url:
            story.append(Paragraph(f"Portfolio: {_safe(profile.website_url.removeprefix('https://').removeprefix('http://'))}", contact_style))

        summary = profile.resume_summary.strip() or profile.bio.strip()
        if summary:
            story.append(Paragraph('Personal Profile', section_style))
            story.append(_paragraph(summary, body_style))

    grouped_skills = {}
    category_order = {'Frontend': 0, 'Backend': 1, 'Database': 2, 'DevOps & Tools': 3, 'Other': 4}
    for skill in skills:
        grouped_skills.setdefault(skill.get_category_display(), []).append(skill.name)
    if grouped_skills:
        story.append(Paragraph('Technical Skills', section_style))
        for category, names in sorted(grouped_skills.items(), key=lambda item: category_order.get(item[0], 5)):
            label = {
                'Frontend': 'Front-End', 'Backend': 'Back-End',
                'Database': 'Databases', 'DevOps & Tools': 'Tools & Technologies',
            }.get(category, category)
            story.append(Paragraph(f"• <b>{_safe(label)}:</b> {', '.join(map(_safe, names))}", bullet_style))

    ordered_experiences = list(experiences)
    technical_experiences = [item for item in ordered_experiences if item.cv_section == 'work']
    other_experiences = [item for item in ordered_experiences if item.cv_section == 'other']

    def add_experience_section(title, entries):
        if not entries:
            return
        story.append(Paragraph(title, section_style))
        for item in entries:
            title_line = f"{_safe(item.role)} | {_safe(item.company)} ({_safe(item.duration_label)})"
            group = [Paragraph(title_line, role_style)]
            group.extend(bullet(line) for line in item.description_bullets)
            story.append(KeepTogether(group))

    add_experience_section('Work Experience', technical_experiences)
    if technical_experiences and other_experiences:
        story.append(PageBreak())
    add_experience_section('Other Work Experience', other_experiences)

    if education:
        story.append(Paragraph('Education', section_style))
        for item in education:
            group = [Paragraph(_safe(item.degree), role_style), _paragraph(item.institution, small_style), _paragraph(item.year_label, small_style)]
            if item.description:
                group.append(_paragraph(item.description, small_style))
            story.append(KeepTogether(group))

    if profile and profile.leadership_volunteering.strip():
        story.append(Paragraph('Leadership and Volunteering', section_style))
        for line in profile.leadership_volunteering.splitlines():
            if line.strip():
                story.append(_paragraph(line.strip(), small_style))

    if profile and profile.interests.strip():
        story.append(Paragraph('Hobbies and Interests', section_style))
        story.append(_paragraph(profile.interests.strip(), body_style))

    story.append(Paragraph('References', section_style))
    story.append(_paragraph('Available upon request.', small_style))
    document.build(story)
    return buffer.getvalue()
