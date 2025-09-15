@echo off
echo Pushing Muninn to GitHub...
echo.

REM Create .gitignore to protect sensitive files
echo .env > .gitignore
echo *.db >> .gitignore
echo audio_files/ >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore

echo ✓ Created .gitignore to protect sensitive files
echo.

REM Stage all files
git add .
echo ✓ Staged all files
echo.

REM Commit with message
git commit -m "Complete Muninn voice assistant for Dad's 70th birthday - Custom wake word detection with trained Porcupine model - Family member voice message recording and playback - NeoPixel LED animations for visual feedback - SQLite database for message storage and retrieval - Automatic hardware detection (Pi vs development mode) - Voice commands: record, play [family member], stop - Supports 15 family members with individual LED sections - Ready for Raspberry Pi 5 with Voice Bonnet deployment"
echo ✓ Created commit
echo.

REM Push to GitHub
git push -u origin main
echo ✓ Pushed to GitHub!
echo.

echo Complete! Check https://github.com/bwyatt92/muninn.git
pause