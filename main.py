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
    from rich.console import Console
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

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


class QuickPiCam:
    def __init__(self, output_dir="photos"):
        self.model = Model(output_dir=Path(output_dir))
        self.model.output_dir.mkdir(exist_ok=True)
        self.console = Console() if RICH_AVAILABLE else None
        self.running = True
        
    def init_camera(self):
        try:
            self.model.camera_status = "Detecting camera..."
            self.render()
            time.sleep(0.5)
            
            if not PICAMERA_AVAILABLE:
                self.model.camera_status = "❌ picamera2 not found!"
                return False
            
            self.model.camera_status = "Initializing picamera2..."
            self.render()
            self.model.camera = Picamera2()
            
            self.model.camera_status = "Configuring camera..."
            self.render()
            self.model.camera.configure(self.model.camera.create_still_configuration())
            
            self.model.camera_status = "Starting camera..."
            self.render()
            self.model.camera.start()
            time.sleep(2)
            
            self.model.camera_ready = True
            self.model.camera_status = "✅ Ready"
            return True
            
        except Exception as e:
            self.model.camera_status = f"❌ Error: {str(e)}"
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
        self.render()
        
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
            print(f"❌ Capture failed: {e}")
            return False
        finally:
            self.model.is_capturing = False
    
    def view_rich(self):
        status_color = "green" if self.model.camera_ready else "red"
        status_icon = "🟢" if self.model.camera_ready else "🔴"
        
        content = f"""[bold blue]📷 picam-ui[/bold blue] | {status_icon} [{status_color}]{self.model.camera_status}[/{status_color}]

[bold]📊 Session:[/bold] [green]{self.model.session_count}[/green]  [bold]Total:[/bold] [blue]{self.model.total_count}[/blue]  [bold]Last:[/bold] [yellow]{self.model.last_photo}[/yellow]

{'[bold red]📸 CAPTURING...[/bold red]' if self.model.is_capturing else '[bold green]🎯 READY[/bold green]'}

[bold]📸 Recent Photos:[/bold]"""
        
        if self.model.recent_photos:
            for photo in self.model.recent_photos[-3:]:
                content += f"\n• {photo}"
        else:
            content += "\n[dim]No photos yet...[/dim]"
            
        content += "\n\n[green]SPACE[/green] - Capture | [yellow]R[/yellow] - Refresh | [red]Q[/red] - Quit"
        
        panel = Panel(content, box=box.ROUNDED, padding=(1, 2))
        self.console.print(panel)
    
    def view_simple(self) -> str:
        status_icon = "🟢" if self.model.camera_ready else "🔴"
        capture_status = "📸 CAPTURING..." if self.model.is_capturing else "🎯 READY"
        
        recent = self.model.recent_photos[-3:] if self.model.recent_photos else []
        recent_lines = [f"  • {photo}" for photo in recent]
        while len(recent_lines) < 3:
            recent_lines.append("")
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║ 📷 picam-ui                                                   ║
║ {status_icon} {self.model.camera_status:<50} ║
╠══════════════════════════════════════════════════════════════╣
║ 📊 Session: {self.model.session_count:<3} Total: {self.model.total_count:<3} Last: {self.model.last_photo:<25} ║
║                                                              ║
║ {capture_status:<30}                              ║
║                                                              ║
║ 📸 Recent Photos:                                            ║
║{recent_lines[0]:<62}║
║{recent_lines[1]:<62}║
║{recent_lines[2]:<62}║
╠══════════════════════════════════════════════════════════════╣
║ SPACE - Capture | R - Refresh | Q - Quit                    ║
╚══════════════════════════════════════════════════════════════╝
        """
    
    def render(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
        if RICH_AVAILABLE and self.console:
            self.view_rich()
        else:
            print(self.view_simple())
    
    def handle_input(self, key: str):
        key = key.lower()
        
        if key in ['q', '\x03']:
            self.running = False
        elif key == ' ':
            if self.capture_photo():
                pass
        elif key == 'r':
            self.update_stats()
        
        self.render()
    
    def run(self):
        print("🚀 Starting picam-ui...")
        
        if not self.init_camera():
            print("Failed to initialize camera. Exiting.")
            return
        
        self.update_stats()
        self.render()
        
        try:
            import termios
            import tty
            
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            
            try:
                tty.setraw(fd)
                while self.running:
                    key = sys.stdin.read(1)
                    self.handle_input(key)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                
        except ImportError:
            while self.running:
                try:
                    key = input("\nPress SPACE to capture, R to refresh, Q to quit: ").strip()
                    self.handle_input(key)
                except KeyboardInterrupt:
                    break
        
        if self.model.camera:
            try:
                self.model.camera.stop()
            except:
                pass
        
        print("\n👋 Goodbye!")


def main():
    output_dir = "photos"
    if len(sys.argv) > 1:
        output_dir = sys.argv[1]
    
    app = QuickPiCam(output_dir)
    app.run()


if __name__ == "__main__":
    main() 