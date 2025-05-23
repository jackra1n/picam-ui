#!/usr/bin/env python3

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False

try:
    from textual.app import App
    from textual.widgets import Static
    from textual.containers import Container
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

@dataclass
class Model:
    camera: Optional[object] = None
    camera_ready: bool = False
    camera_status: str = "Initializing..."
    session_count: int = 0
    total_count: int = 0
    last_photo: str = "None"
    recent_photos: list = None
    output_dir: Path = Path("photos")
    is_capturing: bool = False
    
    def __post_init__(self):
        if self.recent_photos is None:
            self.recent_photos = []


class PicamUI(App):
    CSS = """
    Screen {
        background: #1e1e1e;
    }
    
    .header {
        height: 3;
        text-align: center;
        background: #2d2d2d;
        color: #87ceeb;
    }
    
    .content {
        padding: 1;
    }
    
    .status {
        height: 2;
        margin-bottom: 1;
    }
    
    .stats {
        height: 3;
        margin-bottom: 1;
    }
    
    .ready {
        height: 2;
        margin-bottom: 1;
    }
    
    .photos {
        height: 7;
        margin-bottom: 1;
    }
    
    .controls {
        height: 2;
        text-align: center;
        background: #2d2d2d;
    }
    """
    
    def __init__(self, output_dir="photos"):
        super().__init__()
        self.model = Model(output_dir=Path(output_dir))
        self.model.output_dir.mkdir(exist_ok=True)
        
    def compose(self):
        yield Container(
            Static("📷 picam-ui", classes="header"),
            Container(
                Static("", id="status", classes="status"),
                Static("", id="stats", classes="stats"), 
                Static("", id="ready", classes="ready"),
                Static("", id="photos", classes="photos"),
                classes="content"
            ),
            Static("SPACE - Capture | R - Refresh | Q - Quit", classes="controls")
        )
    
    def on_mount(self):
        self.init_camera()
        
    def init_camera(self):
        try:
            self.model.camera_status = "Detecting camera..."
            self.update_display()
            time.sleep(0.5)
            
            if not PICAMERA_AVAILABLE:
                self.model.camera_status = "❌ picamera2 not found!"
                self.update_display()
                return False
            
            self.model.camera_status = "Initializing picamera2..."
            self.update_display()
            self.model.camera = Picamera2()
            
            self.model.camera_status = "Configuring camera..."
            self.update_display()
            self.model.camera.configure(self.model.camera.create_still_configuration())
            
            self.model.camera_status = "Starting camera..."
            self.update_display()
            self.model.camera.start()
            time.sleep(2)
            
            self.model.camera_ready = True
            self.model.camera_status = "✅ Ready"
            self.update_stats()
            self.update_display()
            return True
            
        except Exception as e:
            self.model.camera_status = f"❌ Error: {str(e)}"
            self.update_display()
            return False
    
    def update_stats(self):
        if self.model.output_dir.exists():
            photo_files = list(self.model.output_dir.glob("*.jpg"))
            self.model.total_count = len(photo_files)
            
            if photo_files:
                latest = max(photo_files, key=lambda p: p.stat().st_mtime)
                self.model.last_photo = latest.name
        else:
            self.model.total_count = 0
            self.model.last_photo = "None"
    
    def capture_photo(self):
        if not self.model.camera_ready or self.model.is_capturing:
            return False
        
        self.model.is_capturing = True
        self.update_display()
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.model.session_count += 1
            filename = f"photo_{timestamp}_{self.model.session_count:03d}.jpg"
            filepath = self.model.output_dir / filename
            
            self.model.camera.capture_file(str(filepath))
            
            self.model.recent_photos.append(filename)
            if len(self.model.recent_photos) > 5:
                self.model.recent_photos.pop(0)
            
            self.update_stats()
            return True
            
        except Exception as e:
            self.notify(f"❌ Capture failed: {e}")
            return False
        finally:
            self.model.is_capturing = False
            self.update_display()
    
    def update_display(self):
        status_icon = "🟢" if self.model.camera_ready else "🔴"
        
        # Status
        self.query_one("#status").update(f"{status_icon} {self.model.camera_status}")
        
        # Stats
        stats_text = f"📊 Session: {self.model.session_count}  Total: {self.model.total_count}\n📁 Last: {self.model.last_photo}"
        self.query_one("#stats").update(stats_text)
        
        # Ready status
        if self.model.is_capturing:
            self.query_one("#ready").update("📸 CAPTURING...")
        else:
            ready_text = "🎯 READY" if self.model.camera_ready else "⏳ INITIALIZING"
            self.query_one("#ready").update(ready_text)
        
        # Recent photos
        photos_text = "📸 Recent Photos:\n"
        if self.model.recent_photos:
            for photo in self.model.recent_photos[-5:]:
                photos_text += f"  • {photo}\n"
        else:
            photos_text += "  No photos yet..."
        self.query_one("#photos").update(photos_text)
    
    def on_key(self, event):
        if event.key == "q":
            self.exit()
        elif event.key == "space":
            self.capture_photo()
        elif event.key == "r":
            self.update_stats()
            self.update_display()
    
    def on_exit(self):
        if self.model.camera:
            try:
                self.model.camera.stop()
            except:
                pass


def main():
    if not TEXTUAL_AVAILABLE:
        print("❌ textual package not found! Please install: pip install textual")
        sys.exit(1)
    
    output_dir = "photos"
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    
    app = PicamUI(output_dir)
    app.run()


if __name__ == "__main__":
    main() 