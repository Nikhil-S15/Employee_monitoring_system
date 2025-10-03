import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  Camera, 
  Users, 
  Clock, 
  Download,
  Play,
  Square,
  AlertCircle,
  CheckCircle2,
  XCircle
} from 'lucide-react';
import { 
  PieChart, 
  Pie, 
  Cell, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

// Color scheme for emotions
const EMOTION_COLORS = {
  happy: '#10b981',
  sad: '#3b82f6',
  angry: '#ef4444',
  surprise: '#f59e0b',
  fear: '#8b5cf6',
  neutral: '#6b7280',
  disgust: '#84cc16'
};



function App() {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [currentDetection, setCurrentDetection] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [recentDetections, setRecentDetections] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cameraFrame, setCameraFrame] = useState(null);
  const websocket = useRef(null);

  // Initialize WebSocket connection
  useEffect(() => {
    if (isMonitoring) {
      connectWebSocket();
    } else {
      disconnectWebSocket();
    }

    return () => {
      disconnectWebSocket();
    };
  }, [isMonitoring]);

  // Fetch initial data
  useEffect(() => {
    fetchAnalytics();
    fetchRecentDetections();
    
    // Refresh analytics every 30 seconds
    const interval = setInterval(() => {
      if (isMonitoring) {
        fetchAnalytics();
        fetchRecentDetections();
      }
    }, 30000);

    return () => clearInterval(interval);
  }, [isMonitoring]);

  
 // Add this to your existing App.jsx, around line 40-50:

// Mock data for when camera is not available
const generateMockFrame = () => {
  const canvas = document.createElement('canvas');
  canvas.width = 640;
  canvas.height = 480;
  const ctx = canvas.getContext('2d');
  
  // Create a simple placeholder image
  ctx.fillStyle = '#1f2937';
  ctx.fillRect(0, 0, 640, 480);
  ctx.fillStyle = '#ffffff';
  ctx.font = '24px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('Camera Not Available', 320, 240);
  ctx.font = '16px Arial';
  ctx.fillText('Using Demo Mode', 320, 270);
  
  return canvas.toDataURL('image/jpeg');
};

// Then update the WebSocket connection part:
const connectWebSocket = () => {
  try {
    websocket.current = new WebSocket(`${WS_URL}/ws/detections`);
    
    websocket.current.onopen = () => {
      console.log('WebSocket connected');
      setError(null);
    };
    
    websocket.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      // Handle missing camera gracefully
      if (data.frame) {
        setCameraFrame(`data:image/jpeg;base64,${data.frame}`);
      } else if (data.capabilities && !data.capabilities.opencv) {
        // Use mock frame if OpenCV is not available
        setCameraFrame(generateMockFrame());
      }
      
      // Update current detection
      setCurrentDetection({
        isPresent: data.is_present,
        emotion: data.emotion,
        confidence: data.confidence,
        timestamp: data.timestamp,
        capabilities: data.capabilities
      });

      // Create detection log in database
      if (data.is_present !== undefined) {
        createDetectionLog(data);
      }
    };
    
  
      
      websocket.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('Failed to connect to camera feed');
      };
      
      websocket.current.onclose = () => {
        console.log('WebSocket disconnected');
      };
    } catch (err) {
      console.error('WebSocket connection failed:', err);
      setError('WebSocket connection failed');
    }
  };

  const disconnectWebSocket = () => {
    if (websocket.current) {
      websocket.current.close();
      websocket.current = null;
    }
    setCameraFrame(null);
    setCurrentDetection(null);
  };

  const createDetectionLog = async (data) => {
    try {
      await fetch(`${API_BASE}/api/detection?employee_id=EMP001`, {
        method: 'POST'
      });
    } catch (err) {
      console.error('Failed to create detection log:', err);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/analytics?employee_id=EMP001&days=1`);
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    }
  };

  const fetchRecentDetections = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/detections?employee_id=EMP001&limit=10`);
      if (response.ok) {
        const data = await response.json();
        setRecentDetections(data);
      }
    } catch (err) {
      console.error('Failed to fetch recent detections:', err);
    }
  };

  const toggleMonitoring = () => {
    setIsMonitoring(!isMonitoring);
    setError(null);
  };

  const exportReport = async (format) => {
    try {
      const response = await fetch(`${API_BASE}/api/export/${format}?employee_id=EMP001&days=1`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `employee_report_${new Date().toISOString().split('T')[0]}.${format}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error(`Failed to export ${format}:`, err);
      setError(`Failed to export ${format.toUpperCase()} report`);
    }
  };
  

  // Prepare chart data
  const emotionData = analytics?.emotion_distribution ? 
    Object.entries(analytics.emotion_distribution).map(([emotion, count]) => ({
      name: emotion.charAt(0).toUpperCase() + emotion.slice(1),
      value: count,
      color: EMOTION_COLORS[emotion] || EMOTION_COLORS.neutral
    })) : [];

  const barChartData = analytics?.emotion_distribution ?
    Object.entries(analytics.emotion_distribution).map(([emotion, count]) => ({
      emotion: emotion.charAt(0).toUpperCase() + emotion.slice(1),
      count: count,
      fill: EMOTION_COLORS[emotion] || EMOTION_COLORS.neutral
    })) : [];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Activity className="h-8 w-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Employee Monitoring System
                </h1>
                <p className="text-sm text-gray-500">
                  Real-time presence and emotion detection
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-400'}`} />
                <span className="text-sm text-gray-600">
                  {isMonitoring ? 'Live Monitoring' : 'Monitoring Stopped'}
                </span>
              </div>
              
              <button
                onClick={toggleMonitoring}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  isMonitoring 
                    ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                }`}
              >
                {isMonitoring ? (
                  <>
                    <Square className="h-4 w-4" />
                    <span>Stop Monitoring</span>
                  </>
                ) : (
                  <>
                    <Play className="h-4 w-4" />
                    <span>Start Monitoring</span>
                  </>
                )}
              </button>

              <div className="flex space-x-2">
                <button
                  onClick={() => exportReport('csv')}
                  className="flex items-center space-x-2 px-3 py-2 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
                >
                  <Download className="h-4 w-4" />
                  <span className="text-sm">CSV</span>
                </button>
                <button
                  onClick={() => exportReport('pdf')}
                  className="flex items-center space-x-2 px-3 py-2 bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors"
                >
                  <Download className="h-4 w-4" />
                  <span className="text-sm">PDF</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Error Alert */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
            <AlertCircle className="h-5 w-5 text-red-500" />
            <span className="text-red-700">{error}</span>
            <button
              onClick={() => setError(null)}
              className="ml-auto text-red-500 hover:text-red-700"
            >
              <XCircle className="h-5 w-5" />
            </button>
          </div>
        </div>
      )}

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Live Monitoring Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Camera Feed */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Camera className="h-5 w-5 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">Live Camera Feed</h2>
            </div>
            
            <div className="aspect-video bg-gray-900 rounded-lg overflow-hidden flex items-center justify-center">
              {cameraFrame ? (
                <img 
                  src={cameraFrame} 
                  alt="Live camera feed" 
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="text-gray-500 text-center">
                  <Camera className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>{isMonitoring ? 'Starting camera...' : 'Camera feed inactive'}</p>
                </div>
              )}
            </div>
          </div>

          {/* Current Detection */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center space-x-2 mb-4">
              <Activity className="h-5 w-5 text-gray-600" />
              <h2 className="text-lg font-semibold text-gray-900">Current Detection</h2>
            </div>
            
            {currentDetection ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">Status</span>
                  <div className="flex items-center space-x-2">
                    {currentDetection.isPresent ? (
                      <>
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                        <span className="text-green-700 font-medium">Present</span>
                      </>
                    ) : (
                      <>
                        <XCircle className="h-5 w-5 text-red-500" />
                        <span className="text-red-700 font-medium">Not Present</span>
                      </>
                    )}
                  </div>
                </div>

                {currentDetection.isPresent && (
                  <>
                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Emotion</span>
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: EMOTION_COLORS[currentDetection.emotion] || EMOTION_COLORS.neutral }}
                        />
                        <span className="font-medium text-gray-900 capitalize">
                          {currentDetection.emotion || 'Unknown'}
                        </span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                      <span className="text-sm font-medium text-gray-700">Confidence</span>
                      <span className="font-medium text-gray-900">
                        {currentDetection.confidence ? `${currentDetection.confidence.toFixed(1)}%` : 'N/A'}
                      </span>
                    </div>
                  </>
                )}

                <div className="text-xs text-gray-500 text-center">
                  Last updated: {new Date(currentDetection.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No detection data available</p>
                <p className="text-sm">Start monitoring to see real-time data</p>
              </div>
            )}
          </div>
        </div>

        {/* Analytics Cards */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center space-x-3">
                <Users className="h-8 w-8 text-blue-500" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Presence Rate</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analytics.presence_percentage.toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center space-x-3">
                <Clock className="h-8 w-8 text-green-500" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Working Hours</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analytics.working_hours.toFixed(1)}h
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center space-x-3">
                <Activity className="h-8 w-8 text-purple-500" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Detections</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {analytics.total_detections}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm border p-6">
              <div className="flex items-center space-x-3">
                <div 
                  className="w-8 h-8 rounded-full flex items-center justify-center"
                  style={{ 
                    backgroundColor: emotionData[0]?.color || EMOTION_COLORS.neutral 
                  }}
                >
                  <Activity className="h-4 w-4 text-white" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-600">Top Emotion</p>
                  <p className="text-2xl font-bold text-gray-900 capitalize">
                    {emotionData[0]?.name.toLowerCase() || 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Charts Section */}
        {analytics && Object.keys(analytics.emotion_distribution).length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {/* Pie Chart */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Emotion Distribution</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={emotionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {emotionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Bar Chart */}
            <div className="bg-white rounded-xl shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Emotion Frequency</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={barChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="emotion" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="count" name="Detection Count">
                      {barChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}

        {/* Recent Detections Table */}
        <div className="bg-white rounded-xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Detections</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Time</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Status</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Emotion</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {recentDetections.map((detection, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {new Date(detection.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      {detection.is_present ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Present
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          Not Present
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ 
                            backgroundColor: EMOTION_COLORS[detection.emotion] || EMOTION_COLORS.neutral 
                          }} 
                        />
                        <span className="text-sm text-gray-600 capitalize">
                          {detection.emotion || 'N/A'}
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4 text-sm text-gray-600">
                      {detection.confidence ? `${detection.confidence.toFixed(1)}%` : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600">
              Employee Monitoring System v1.0.0
            </p>
            <p className="text-sm text-gray-600">
              Real-time AI-powered analytics
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;