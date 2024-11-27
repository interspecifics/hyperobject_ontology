#!/bin/bash

# Hide cursor in console by adding it to .bashrc if not already there
if ! grep -q '\033\[?25l' ~/.bashrc; then
    echo -e '\033[?25l' >> ~/.bashrc
fi

# Hide cursor in X11 using existing tools
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/hide_cursor.desktop << EOF
[Desktop Entry]
Type=Application
Name=Hide Cursor
Exec=sh -c 'xset s off; xset -dpms; xset s noblank; xsetroot -cursor_name blank'
EOF
chmod +x ~/.config/autostart/hide_cursor.desktop

# Configure ALSA for HDMI audio (simpler configuration)
sudo tee /etc/asound.conf << EOF
defaults.pcm.card 1
defaults.pcm.device 0
defaults.ctl.card 1
EOF

# Add required environment variables if not already present
if ! grep -q "DISPLAY" /etc/environment; then
    echo "DISPLAY=:0" | sudo tee -a /etc/environment
fi

if ! grep -q "XAUTHORITY" /etc/environment; then
    echo "XAUTHORITY=/home/pi/.Xauthority" | sudo tee -a /etc/environment
fi

echo "Environment setup complete. Please reboot for changes to take effect." 