# Doc Harvest 🌾

A proof-of-concept application to test incremental Google Doc ID patterns and validate document access/extraction through systematic ID incrementation.

## Overview

Doc Harvest explores whether Google Document IDs follow discoverable sequential patterns by testing incremental variations of known working document IDs. The application provides both a FastAPI backend for document analysis and a React frontend for interactive testing.

## Features

- **Document ID Analysis**: Analyze the structure and patterns of Google Doc IDs
- **Incremental Testing**: Test systematic variations of document IDs using multiple strategies:
  - Last character incrementation
  - Last digit incrementation  
  - Last letter incrementation
  - All position incrementation
- **Batch Processing**: Test hundreds of ID variations with configurable rate limiting
- **Content Extraction**: Extract document titles and content previews from accessible documents
- **Interactive Interface**: Clean React frontend for testing and result visualization

## Architecture

### Backend (FastAPI)
- **Document Analyzer**: Core logic for ID pattern analysis and incrementation
- **API Endpoints**: RESTful endpoints for testing and analysis
- **Rate Limiting**: Configurable delays to respect Google's terms of service
- **Content Extraction**: HTTP-based document access and parsing

### Frontend (React + Vite)
- **Testing Interface**: Input forms for base IDs and testing parameters
- **Results Visualization**: Tabbed interface showing discovered documents
- **Progress Tracking**: Real-time updates during batch testing
- **Document Preview**: Quick access to discovered documents

## Getting Started

### Prerequisites
- Python 3.12+ with Poetry
- Node.js 18+ with npm/pnpm
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/bomatson/doc-harvest.git
   cd doc-harvest
   ```

2. **Set up the backend**
   ```bash
   cd google-docs-backend
   poetry install
   poetry run fastapi dev app/main.py
   ```

3. **Set up the frontend**
   ```bash
   cd google-docs-frontend
   npm install
   npm run dev
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage

1. **Enter a Base Document ID**: Use a known working Google Doc ID as your starting point
2. **Configure Testing Parameters**: 
   - Set max increments (10-1000+)
   - Choose increment strategies
   - Set delay between requests (recommended: 1+ seconds)
3. **Run Tests**: Click "Test Incremental IDs" to discover new documents
4. **Analyze Results**: Review discovered documents in the Results tab

## Example Document IDs

The following public Google Docs can be used as base IDs for testing:
- `11ql80LUVCpuk-tyW0oZ0Pf-v0NmEbXuC5115fSAX-io`
- `1ctvfdHRoRxdH87W7GlfKqQWOn0PbtrMjToHvD0x7DQc`
- `1kWuNeZzDg01f6nWDmFvpUdT646HZJxrSIJ7F8pwf0po`

## API Endpoints

- `POST /analyze/{document_id}` - Analyze document ID structure
- `POST /test-document/{document_id}` - Test single document access
- `POST /test-documents` - Batch test multiple documents
- `POST /generate-increments/{base_id}` - Generate incremented ID variations
- `POST /test-increments` - Test incremented document variations
- `GET /known-documents` - Get list of known working document IDs

## Technical Details

### ID Incrementation Strategies

1. **Last Character**: Increment the final character (a→b, 1→2, etc.)
2. **Last Digit**: Find and increment the last numeric digit
3. **Last Letter**: Find and increment the last alphabetic character
4. **All Positions**: Try incrementing each character position individually

### Rate Limiting

The application implements configurable delays between requests to respect Google's infrastructure:
- Default: 1 second between requests
- Recommended for large batches: 2+ seconds
- Exponential backoff on rate limit errors

### Content Extraction

Documents are accessed via direct HTTP requests to Google Docs URLs:
- Public document URLs (no authentication required)
- HTML parsing for title and content extraction
- Error handling for private/deleted documents

## Development

### Project Structure
```
doc-harvest/
├── google-docs-backend/          # FastAPI backend
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── api.py               # API endpoints
│   │   └── document_analyzer.py # Core analysis logic
│   └── pyproject.toml           # Python dependencies
├── google-docs-frontend/         # React frontend
│   ├── src/
│   │   ├── App.tsx              # Main application component
│   │   └── components/ui/       # UI components
│   └── package.json             # Node.js dependencies
└── README.md                    # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Legal & Ethics

This tool is designed for educational and research purposes to understand document ID patterns. Users must:
- Only access publicly available documents
- Respect Google's Terms of Service
- Implement appropriate rate limiting
- Not attempt to access private or restricted content

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with FastAPI and React
- Uses Tailwind CSS and shadcn/ui for styling
- Developed as a proof-of-concept for document discovery research

---

**⚠️ Disclaimer**: This tool is for educational purposes only. Always respect website terms of service and implement appropriate rate limiting when making automated requests.
