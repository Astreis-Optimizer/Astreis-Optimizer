# Astreis - All In One PC Optimizer

A comprehensive PC optimization tool built with PySide6 that provides system optimization, AI chat assistance, and performance monitoring.

## Features

- **System Optimization**: Power plan optimization, appearance settings, and drive defragmentation
- **AI Chat Assistant**: Integrated Groq AI chatbot for PC optimization advice
- **System Monitoring**: Real-time system information display
- **Modern UI**: Beautiful, responsive interface with dark theme support
- **Admin Privileges**: Automatic elevation for system-level optimizations

## Installation

### Prerequisites

- Windows 10/11
- Python 3.8 or higher
- Administrator privileges (required for optimization features)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Astreis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

### Main Interface

The application features three main sections:

1. **Home**: System information and overview
2. **AI Chatbot**: Interactive AI assistant for optimization advice
3. **Optimize PC**: System optimization tools

### Optimization Features

- **Power Plan Optimization**: Creates and configures a high-performance power plan
- **Appearance Optimization**: Disables visual effects for better performance
- **Drive Defragmentation**: Analyzes and optimizes drive performance

### AI Chat Assistant

The integrated AI chatbot can provide:
- Optimization recommendations
- Troubleshooting advice
- Performance tips
- System maintenance guidance

## Dependencies

- **PySide6**: Qt framework for the GUI
- **groq**: AI chat functionality
- **psutil**: System monitoring
- **py-cpuinfo**: CPU information
- **wmi**: Windows Management Instrumentation
- **pywin32**: Windows API access

## Development

### Project Structure

```
Astreis/
├── main.py                 # Application entry point
├── gui/                    # GUI components
│   ├── core/              # Core functionality
│   ├── uis/               # User interface definitions
│   └── widgets/           # Custom widgets
├── AstreisFunc/           # Main functionality module
└── requirements.txt       # Python dependencies
```

### Building

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open an issue on the GitHub repository.

## Disclaimer

This tool performs system-level optimizations. Use at your own risk and ensure you have proper backups before making system changes. 