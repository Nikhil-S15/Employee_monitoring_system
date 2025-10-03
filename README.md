# Employee Monitoring System

A comprehensive real-time employee presence and emotion detection system built with FastAPI, React, and advanced computer vision technologies. This system provides intelligent workplace analytics through AI-powered emotion recognition and real-time monitoring capabilities.

## 🚀 Features

### 🤖 AI-Powered Emotion Recognition
- **Multi-Model Emotion Detection**: Hybrid approach using FER, DeepFace, and enhanced fallback systems
- **Real-time Facial Analysis**: Live emotion tracking with confidence scoring
- **Emotion Stability Buffer**: Smart emotion persistence to prevent rapid switching
- **ML Model Fallbacks**: Graceful degradation between FER, DeepFace, and rule-based detection

### 👥 Employee Monitoring
- **Real-time Face Detection**: Advanced face detection using OpenCV and Haar cascades
- **Presence Tracking**: Accurate employee presence/absence monitoring
- **Live Video Streaming**: WebSocket-based real-time video feed with overlay data
- **Multi-Camera Support**: Automatic camera detection and configuration

### 📊 Analytics & Insights
- **Comprehensive Dashboard**: Real-time charts and metrics visualization
- **Emotion Distribution**: Detailed emotion analytics and trends
- **Working Hours Calculation**: Automated presence duration tracking
- **Historical Data**: Time-based filtering and trend analysis

### 🔧 Technical Features
- **RESTful API**: Fully documented FastAPI backend with Swagger UI
- **WebSocket Support**: Real-time bidirectional communication
- **Export Functionality**: CSV and PDF report generation
- **Database Persistence**: SQLite with SQLAlchemy ORM
- **CORS Enabled**: Cross-origin resource sharing support

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework with automatic API documentation
- **OpenCV** - Computer vision and real-time image processing
- **FER** - Facial Expression Recognition with pre-trained ML models
- **DeepFace** - Deep learning for advanced emotion analysis
- **SQLAlchemy** - Database ORM with migration support
- **SQLite** - Lightweight database (easily switchable to PostgreSQL)
- **Pydantic** - Data validation and settings management
- **WebSockets** - Real-time communication protocol

### Frontend
- **React 18** - Modern React with hooks and functional components
- **Vite** - Lightning-fast build tool and development server
- **Tailwind CSS** - Utility-first CSS framework for responsive design
- **Recharts** - Composable charting library for analytics
- **Lucide React** - Beautiful, consistent icon library
- **Axios** - Promise-based HTTP client for API calls
- **WebSocket Client** - Real-time data streaming

### AI/ML Components
- **FER (Facial Expression Recognition)** - Primary emotion detection
- **DeepFace** - Backup deep learning model
- **MediaPipe** - Alternative face detection (fallback)
- **TensorFlow** - ML framework backend
- **MTCNN** - Multi-task Cascaded CNN for face detection

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Camera device (for real-time detection)

### Quick Start (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd employee-monitoring-system
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start the backend server
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   
   # Start the development server
   npm run dev
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Installation

#### Backend Dependencies
```bash
cd backend
pip install fastapi uvicorn python-multipart
pip install opencv-python numpy sqlalchemy python-dotenv
pip install fer deepface mediapipe tensorflow
```

#### Frontend Dependencies
```bash
cd frontend
npm install react react-dom
npm install @vitejs/plugin-react vite
npm install tailwindcss postcss autoprefixer
npm install recharts lucide-react axios
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./employee_monitoring.db
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

### Camera Configuration
The system automatically detects available cameras. For manual configuration:

```python
# In main.py - Camera settings
self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

## 🎯 Usage

### Real-time Monitoring
1. **Start Detection**: Navigate to the dashboard to begin real-time monitoring
2. **View Live Feed**: Watch the real-time video stream with emotion overlays
3. **Analyze Emotions**: Monitor emotion distribution and confidence scores
4. **Track Presence**: View employee presence statistics and working hours

### API Endpoints

#### Core Endpoints
- `GET /` - API root with system status
- `GET /api/health` - Health check and capability report
- `POST /api/detection` - Capture and log detection
- `GET /api/detections` - Retrieve detection history
- `GET /api/analytics` - Get analytics data

#### Real-time Endpoints
- `GET /api/video_feed` - MJPEG video stream
- `WS /ws/detections` - WebSocket for real-time updates
- `WS /ws/fer-detections` - Enhanced FER WebSocket

#### Export Endpoints
- `GET /api/export/csv` - Export data as CSV
- `GET /api/export/pdf` - Generate PDF reports

### WebSocket Events
```javascript
// Connection
const ws = new WebSocket('ws://localhost:8000/ws/detections');

// Received data structure
{
  "frame": "base64_encoded_image",
  "is_present": true,
  "emotion": "happy",
  "confidence": 85.5,
  "timestamp": "2024-01-15T10:30:00Z",
  "detector": "FER",
  "fer_available": true,
  "buffer_size": 4
}
```

## 📊 Analytics & Metrics

### Key Metrics
- **Presence Percentage**: Overall attendance rate
- **Emotion Distribution**: Breakdown of detected emotions
- **Working Hours**: Calculated presence duration
- **Emotion Stability**: Consistency of emotional states
- **Confidence Scores**: Accuracy metrics for detections

### Data Export
- **CSV Export**: Raw data for external analysis
- **PDF Reports**: Formatted analytics reports
- **Time-based Filtering**: Custom date range exports

## 🔍 Emotion Detection System

### Multi-Layer Architecture
1. **Primary Detection**: FER with MTCNN for high accuracy
2. **Secondary Detection**: DeepFace for backup analysis
3. **Enhanced Fallback**: Rule-based facial feature analysis
4. **Basic Fallback**: Randomized emotional state simulation

### Supported Emotions
- 😊 Happy
- 😐 Neutral 
- 😢 Sad
- 😮 Surprise
- 😠 Angry
- 😨 Fear
- 🤢 Disgust

### Confidence System
- **High Confidence**: >80% - Reliable detection
- **Medium Confidence**: 60-80% - Likely accurate
- **Low Confidence**: <60% - Uncertain detection

## 🛠️ Development

### Project Structure
```
employee-monitoring-system/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── face_analyzer.py        # Emotion detection logic
│   ├── export_routes.py        # Data export endpoints
│   ├── requirements.txt        # Python dependencies
│   └── employee_monitoring.db  # Database (auto-generated)
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/             # Application pages
│   │   ├── hooks/             # Custom React hooks
│   │   └── utils/             # Utility functions
│   ├── package.json
│   └── vite.config.js
└── README.md
```

### Adding New Features
1. **Backend**: Add new endpoints in `main.py`
2. **Frontend**: Create components in `src/components/`
3. **Database**: Update models in `main.py`
4. **AI Models**: Extend `face_analyzer.py`

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests  
cd frontend
npm test
```

## 🚀 Deployment

### Production Build
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm run build
npm run preview
```

### Docker Deployment
```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React
- Write tests for new features
- Update documentation accordingly

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**Camera Not Detected**
```bash
# Check available cameras
python -c "import cv2; print([cv2.VideoCapture(i).isOpened() for i in range(4)])"
```

**FER Import Errors**
```bash
# Reinstall with compatible versions
pip uninstall fer tensorflow
pip install fer tensorflow==2.16.2
```

**WebSocket Connection Issues**
- Check CORS settings
- Verify backend is running on correct port
- Ensure frontend URL matches backend CORS origins

### Performance Optimization
- Reduce frame processing rate in `face_analyzer.py`
- Adjust camera resolution in `main.py`
- Enable/disable ML models based on hardware capabilities

## 📞 Support

For support and questions:
1. Check the [API Documentation](http://localhost:8000/docs)
2. Review the [troubleshooting guide](#troubleshooting)
3. Create an issue in the repository

## 🎉 Acknowledgments

- **OpenCV** community for computer vision tools
- **FER** library for emotion recognition capabilities
- **FastAPI** for the excellent web framework
- **React** team for the frontend library
- **Tailwind CSS** for the utility-first CSS framework

---

**Employee Monitoring System** - Intelligent workplace analytics through AI-powered emotion recognition and real-time monitoring.