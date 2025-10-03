from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from datetime import datetime, timedelta
import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

router = APIRouter()

def generate_csv_report(detections, analytics):
    """Generate CSV report from detections"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Employee Monitoring Report'])
    writer.writerow(['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Write analytics summary
    writer.writerow(['Summary'])
    writer.writerow(['Total Detections:', analytics['total_detections']])
    writer.writerow(['Presence Rate:', f"{analytics['presence_percentage']}%"])
    writer.writerow(['Working Hours:', f"{analytics['working_hours']}h"])
    writer.writerow([])
    
    # Write emotion distribution
    writer.writerow(['Emotion Distribution'])
    for emotion, count in analytics['emotion_distribution'].items():
        writer.writerow([emotion.capitalize(), count])
    writer.writerow([])
    
    # Write detailed detections
    writer.writerow(['Detailed Detection Log'])
    writer.writerow(['Timestamp', 'Employee ID', 'Status', 'Emotion', 'Confidence'])
    
    for detection in detections:
        writer.writerow([
            detection['timestamp'],
            detection['employee_id'],
            'Present' if detection['is_present'] else 'Not Present',
            detection['emotion'] or 'N/A',
            f"{detection['confidence']:.2f}%" if detection['confidence'] else 'N/A'
        ])
    
    output.seek(0)
    return output.getvalue()

def generate_pdf_report(detections, analytics, employee_id):
    """Generate PDF report with charts and tables"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#374151'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph("Employee Monitoring Report", title_style)
    elements.append(title)
    
    # Report metadata
    meta_data = [
        ['Employee ID:', employee_id],
        ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        ['Report Period:', 'Last 24 Hours']
    ]
    
    meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary Section
    summary_heading = Paragraph("Summary Statistics", heading_style)
    elements.append(summary_heading)
    
    summary_data = [
        ['Metric', 'Value'],
        ['Total Detections', str(analytics['total_detections'])],
        ['Presence Rate', f"{analytics['presence_percentage']:.2f}%"],
        ['Working Hours', f"{analytics['working_hours']:.2f}h"],
        ['Most Frequent Emotion', 
         max(analytics['emotion_distribution'].items(), key=lambda x: x[1])[0].capitalize() 
         if analytics['emotion_distribution'] else 'N/A']
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Emotion Distribution Section
    emotion_heading = Paragraph("Emotion Distribution", heading_style)
    elements.append(emotion_heading)
    
    if analytics['emotion_distribution']:
        emotion_data = [['Emotion', 'Count', 'Percentage']]
        total_emotions = sum(analytics['emotion_distribution'].values())
        
        for emotion, count in sorted(analytics['emotion_distribution'].items(), 
                                     key=lambda x: x[1], reverse=True):
            percentage = (count / total_emotions * 100) if total_emotions > 0 else 0
            emotion_data.append([
                emotion.capitalize(),
                str(count),
                f"{percentage:.1f}%"
            ])
        
        emotion_table = Table(emotion_data, colWidths=[2*inch, 2*inch, 2*inch])
        emotion_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(emotion_table)
    else:
        elements.append(Paragraph("No emotion data available", styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Detailed Detection Log
    log_heading = Paragraph("Detailed Detection Log (Latest 20)", heading_style)
    elements.append(log_heading)
    
    if detections:
        log_data = [['Time', 'Status', 'Emotion', 'Confidence']]
        
        for detection in detections[:20]:
            timestamp = datetime.fromisoformat(detection['timestamp']).strftime('%H:%M:%S')
            status = 'Present' if detection['is_present'] else 'Absent'
            emotion = detection['emotion'].capitalize() if detection['emotion'] else 'N/A'
            confidence = f"{detection['confidence']:.1f}%" if detection['confidence'] else 'N/A'
            
            log_data.append([timestamp, status, emotion, confidence])
        
        log_table = Table(log_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        log_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        elements.append(log_table)
    else:
        elements.append(Paragraph("No detection logs available", styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

@router.get("/export/csv")
async def export_csv(
    employee_id: str = "EMP001",
    days: int = 1
):
    """Export detection data as CSV"""
    from main import SessionLocal, DetectionLog
    
    db = SessionLocal()
    try:
        # Get detections
        start_date = datetime.utcnow() - timedelta(days=days)
        detections = db.query(DetectionLog).filter(
            DetectionLog.employee_id == employee_id,
            DetectionLog.timestamp >= start_date
        ).order_by(DetectionLog.timestamp.desc()).all()
        
        # Get analytics
        total_detections = len(detections)
        present_count = sum(1 for d in detections if d.is_present)
        presence_percentage = (present_count / total_detections * 100) if total_detections > 0 else 0
        working_hours = (present_count * 0.5) / 60
        
        emotion_distribution = {}
        for d in detections:
            if d.emotion and d.is_present:
                emotion_distribution[d.emotion] = emotion_distribution.get(d.emotion, 0) + 1
        
        analytics = {
            'total_detections': total_detections,
            'presence_percentage': presence_percentage,
            'working_hours': working_hours,
            'emotion_distribution': emotion_distribution
        }
        
        # Convert to dict format
        detection_dicts = [
            {
                'timestamp': d.timestamp.isoformat(),
                'employee_id': d.employee_id,
                'is_present': d.is_present,
                'emotion': d.emotion,
                'confidence': d.confidence
            }
            for d in detections
        ]
        
        # Generate CSV
        csv_content = generate_csv_report(detection_dicts, analytics)
        
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=employee_report_{employee_id}_{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )
    finally:
        db.close()

@router.get("/export/pdf")
async def export_pdf(
    employee_id: str = "EMP001",
    days: int = 1
):
    """Export detection data as PDF"""
    from main import SessionLocal, DetectionLog
    
    db = SessionLocal()
    try:
        # Get detections
        start_date = datetime.utcnow() - timedelta(days=days)
        detections = db.query(DetectionLog).filter(
            DetectionLog.employee_id == employee_id,
            DetectionLog.timestamp >= start_date
        ).order_by(DetectionLog.timestamp.desc()).all()
        
        if not detections:
            raise HTTPException(status_code=404, detail="No data found for export")
        
        # Get analytics
        total_detections = len(detections)
        present_count = sum(1 for d in detections if d.is_present)
        presence_percentage = (present_count / total_detections * 100)
        working_hours = (present_count * 0.5) / 60
        
        emotion_distribution = {}
        for d in detections:
            if d.emotion and d.is_present:
                emotion_distribution[d.emotion] = emotion_distribution.get(d.emotion, 0) + 1
        
        analytics = {
            'total_detections': total_detections,
            'presence_percentage': presence_percentage,
            'working_hours': working_hours,
            'emotion_distribution': emotion_distribution
        }
        
        # Convert to dict format
        detection_dicts = [
            {
                'timestamp': d.timestamp.isoformat(),
                'employee_id': d.employee_id,
                'is_present': d.is_present,
                'emotion': d.emotion,
                'confidence': d.confidence
            }
            for d in detections
        ]
        
        # Generate PDF
        pdf_buffer = generate_pdf_report(detection_dicts, analytics, employee_id)
        
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=employee_report_{employee_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )
    finally:
        db.close()