"""
KMTronic 4-Channel USB Relay Control Dashboard - Modern Minimalist Style
Features: Clean design, side panel layout, smooth animations
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import time
import threading


class RelayControllerStandalone:
    """Standalone relay controller without external dependencies"""
    
    def __init__(self, com_port, baudrate=9600, timeout=2.5):
        self.com_port = com_port
        self.baudrate = baudrate
        self.timeout = timeout
        self.connection = None
        self.is_connected = False
        
    def connect(self):
        """Open serial connection"""
        try:
            self.connection = serial.Serial(
                port=self.com_port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
                parity=serial.PARITY_NONE,
                timeout=self.timeout
            )
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
            time.sleep(0.5)
            self.is_connected = True
            return True
        except Exception as e:
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass
                self.connection = None
            raise Exception(f"Failed to connect to {self.com_port}: {str(e)}")
    
    def disconnect(self):
        """Close serial connection"""
        if self.connection and self.connection.is_open:
            self.connection.close()
            self.is_connected = False
    
    def turn_on(self, relay_number):
        """Turn ON the specified relay (1-4)"""
        if not self.is_connected or not self.connection:
            raise Exception("Not connected to relay board")
        if not (1 <= relay_number <= 4):
            raise ValueError("Relay number must be between 1 and 4")
        
        try:
            cmd = bytes([0xFF, relay_number, 0x01])
            if self.connection.out_waiting > 0:
                self.connection.reset_output_buffer()
            self.connection.write(cmd)
            self.connection.flush()
            time.sleep(0.3)
        except Exception as e:
            raise Exception(f"Failed to turn on relay {relay_number}: {str(e)}")
    
    def turn_off(self, relay_number):
        """Turn OFF the specified relay (1-4)"""
        if not self.is_connected or not self.connection:
            raise Exception("Not connected to relay board")
        if not (1 <= relay_number <= 4):
            raise ValueError("Relay number must be between 1 and 4")
        
        try:
            cmd = bytes([0xFF, relay_number, 0x00])
            if self.connection.out_waiting > 0:
                self.connection.reset_output_buffer()
            self.connection.write(cmd)
            self.connection.flush()
            time.sleep(0.3)
        except Exception as e:
            raise Exception(f"Failed to turn off relay {relay_number}: {str(e)}")
    
    def get_status(self):
        """Get status of all relays"""
        if not self.is_connected or not self.connection:
            return {}
        
        try:
            if self.connection.in_waiting > 0:
                self.connection.reset_input_buffer()
            
            status_cmd = bytes([0xFF, 0x09, 0x00])
            self.connection.write(status_cmd)
            self.connection.flush()
            time.sleep(0.3)
            
            response = self.connection.read(4)
            
            if len(response) == 4:
                result = {
                    f"R{i}": "ON" if byte == 1 else "OFF"
                    for i, byte in enumerate(response, start=1)
                }
                return result
            return {}
        except Exception:
            return {}
    
    @staticmethod
    def get_available_ports():
        """Get list of available COM ports"""
        return [port.device for port in serial.tools.list_ports.comports()]


class ModernRelayDashboard:
    """Modern minimalist GUI Dashboard for Relay Control"""
    
    # Modern color palette - Light/Professional theme
    COLORS = {
        'bg': '#f5f7fa',
        'sidebar': '#2c3e50',
        'sidebar_hover': '#34495e',
        'card_bg': '#ffffff',
        'border': '#e1e8ed',
        'primary': '#3498db',
        'primary_dark': '#2980b9',
        'success': '#27ae60',
        'success_dark': '#229954',
        'danger': '#e74c3c',
        'danger_dark': '#c0392b',
        'warning': '#f39c12',
        'text_dark': '#2c3e50',
        'text_light': '#7f8c8d',
        'text_white': '#ffffff',
        'relay_on_bg': '#e8f8f5',
        'relay_on_border': '#27ae60',
        'relay_off_bg': '#fadbd8',
        'relay_off_border': '#e74c3c',
        'shadow': '#d5d8dc',
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Relay Control Dashboard")
        self.root.geometry("1000x650")
        self.root.configure(bg=self.COLORS['bg'])
        
        self.controller = None
        self.relay_states = {1: False, 2: False, 3: False, 4: False}
        self.status_update_running = False
        
        self.setup_ui()
        self.refresh_ports()
        
    def setup_ui(self):
        """Setup the modern GUI layout"""
        
        # Main container with sidebar and content
        main_container = tk.Frame(self.root, bg=self.COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left Sidebar for connection controls
        self.create_sidebar(main_container)
        
        # Right Content Area
        self.create_content_area(main_container)
        
    def create_sidebar(self, parent):
        """Create left sidebar with connection settings"""
        sidebar = tk.Frame(parent, bg=self.COLORS['sidebar'], width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo/Title area
        title_frame = tk.Frame(sidebar, bg=self.COLORS['sidebar'])
        title_frame.pack(pady=30)
        
        tk.Label(
            title_frame,
            text="⚡",
            font=('Arial', 40),
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['text_white']
        ).pack()
        
        tk.Label(
            title_frame,
            text="Relay Control",
            font=('Arial', 18, 'bold'),
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['text_white']
        ).pack()
        
        tk.Label(
            title_frame,
            text="KMTronic 4-Channel",
            font=('Arial', 10),
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['text_light']
        ).pack()
        tk.Label(
            title_frame,
            text="Author: Madhava Reddy Yeruva",
            font=('Arial', 10),
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['text_light']
        ).pack()
        # Separator
        tk.Frame(sidebar, bg=self.COLORS['border'], height=1).pack(fill=tk.X, padx=20, pady=20)
        
        # Connection section
        conn_section = tk.Frame(sidebar, bg=self.COLORS['sidebar'])
        conn_section.pack(fill=tk.X, padx=20)
        
        tk.Label(
            conn_section,
            text="CONNECTION",
            font=('Arial', 9, 'bold'),
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['text_light']
        ).pack(anchor='w', pady=(0, 10))
        
        # Port selection
        port_label = tk.Label(
            conn_section,
            text="COM Port",
            font=('Arial', 10),
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['text_white']
        )
        port_label.pack(anchor='w', pady=(5, 2))
        
        port_frame = tk.Frame(conn_section, bg=self.COLORS['sidebar'])
        port_frame.pack(fill=tk.X, pady=(0, 15))
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Sidebar.TCombobox', fieldbackground=self.COLORS['sidebar_hover'])
        
        self.port_combo = ttk.Combobox(
            port_frame, 
            width=18, 
            font=('Arial', 10),
            style='Sidebar.TCombobox'
        )
        self.port_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        refresh_btn = tk.Button(
            port_frame,
            text="↻",
            command=self.refresh_ports,
            font=('Arial', 12, 'bold'),
            bg=self.COLORS['sidebar_hover'],
            fg=self.COLORS['text_white'],
            activebackground=self.COLORS['primary'],
            relief=tk.FLAT,
            cursor='hand2',
            width=3,
            bd=0
        )
        refresh_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Status indicator
        status_frame = tk.Frame(conn_section, bg=self.COLORS['sidebar_hover'], relief=tk.FLAT)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.status_indicator = tk.Label(
            status_frame,
            text="●",
            font=('Arial', 16),
            bg=self.COLORS['sidebar_hover'],
            fg=self.COLORS['text_light']
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(10, 5), pady=10)
        
        self.status_text = tk.Label(
            status_frame,
            text="Disconnected",
            font=('Arial', 10),
            bg=self.COLORS['sidebar_hover'],
            fg=self.COLORS['text_white']
        )
        self.status_text.pack(side=tk.LEFT, pady=10)
        
        # Connect button
        self.connect_btn = tk.Button(
            conn_section,
            text="Connect",
            command=self.toggle_connection,
            font=('Arial', 11, 'bold'),
            bg=self.COLORS['primary'],
            fg=self.COLORS['text_white'],
            activebackground=self.COLORS['primary_dark'],
            activeforeground=self.COLORS['text_white'],
            relief=tk.FLAT,
            cursor='hand2',
            height=2,
            bd=0
        )
        self.connect_btn.pack(fill=tk.X)
        
        # Control All section
        tk.Frame(sidebar, bg=self.COLORS['border'], height=1).pack(fill=tk.X, padx=20, pady=20)
        
        control_section = tk.Frame(sidebar, bg=self.COLORS['sidebar'])
        control_section.pack(fill=tk.X, padx=20)
        
        tk.Label(
            control_section,
            text="QUICK ACTIONS",
            font=('Arial', 9, 'bold'),
            bg=self.COLORS['sidebar'],
            fg=self.COLORS['text_light']
        ).pack(anchor='w', pady=(0, 10))
        
        self.all_on_btn = tk.Button(
            control_section,
            text="⚡ Turn All ON",
            command=self.turn_all_on,
            font=('Arial', 10, 'bold'),
            bg=self.COLORS['success'],
            fg=self.COLORS['text_white'],
            activebackground=self.COLORS['success_dark'],
            relief=tk.FLAT,
            cursor='hand2',
            height=2,
            bd=0,
            state=tk.DISABLED
        )
        self.all_on_btn.pack(fill=tk.X, pady=(0, 8))
        
        self.all_off_btn = tk.Button(
            control_section,
            text="✖ Turn All OFF",
            command=self.turn_all_off,
            font=('Arial', 10, 'bold'),
            bg=self.COLORS['danger'],
            fg=self.COLORS['text_white'],
            activebackground=self.COLORS['danger_dark'],
            relief=tk.FLAT,
            cursor='hand2',
            height=2,
            bd=0,
            state=tk.DISABLED
        )
        self.all_off_btn.pack(fill=tk.X)
        
    def create_content_area(self, parent):
        """Create right content area with relay controls"""
        content = tk.Frame(parent, bg=self.COLORS['bg'])
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header
        header = tk.Frame(content, bg=self.COLORS['bg'])
        header.pack(fill=tk.X, padx=30, pady=20)
        
        tk.Label(
            header,
            text="Relay Channels",
            font=('Arial', 22, 'bold'),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_dark']
        ).pack(anchor='w')
        
        tk.Label(
            header,
            text="Control individual relay channels",
            font=('Arial', 11),
            bg=self.COLORS['bg'],
            fg=self.COLORS['text_light']
        ).pack(anchor='w')
        
        # Relay cards container - Vertical list layout
        cards_container = tk.Frame(content, bg=self.COLORS['bg'])
        cards_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))
        
        self.relay_cards = {}
        
        for i in range(1, 5):
            card = self.create_relay_card_modern(cards_container, i)
            card.pack(fill=tk.X, pady=(0, 15))
            
    def create_relay_card_modern(self, parent, relay_num):
        """Create a modern card for individual relay control"""
        # Card frame with shadow effect
        card_outer = tk.Frame(parent, bg=self.COLORS['shadow'])
        
        card = tk.Frame(
            card_outer,
            bg=self.COLORS['card_bg'],
            relief=tk.FLAT,
            bd=0
        )
        card.pack(padx=1, pady=1, fill=tk.BOTH, expand=True)
        
        # Left side - Info
        left_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Relay number and name
        name_frame = tk.Frame(left_frame, bg=self.COLORS['card_bg'])
        name_frame.pack(anchor='w')
        
        tk.Label(
            name_frame,
            text=f"Channel {relay_num}",
            font=('Arial', 16, 'bold'),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_dark']
        ).pack(side=tk.LEFT)
        
        # Status badge
        status_badge = tk.Label(
            name_frame,
            text="OFF",
            font=('Arial', 9, 'bold'),
            bg=self.COLORS['relay_off_bg'],
            fg=self.COLORS['danger'],
            padx=12,
            pady=4
        )
        status_badge.pack(side=tk.LEFT, padx=15)
        
        # Description
        tk.Label(
            left_frame,
            text=f"Relay output channel #{relay_num}",
            font=('Arial', 10),
            bg=self.COLORS['card_bg'],
            fg=self.COLORS['text_light']
        ).pack(anchor='w', pady=(5, 0))
        
        # Right side - Controls
        right_frame = tk.Frame(card, bg=self.COLORS['card_bg'])
        right_frame.pack(side=tk.RIGHT, padx=25, pady=20)
        
        # Toggle switch button
        toggle_btn = tk.Button(
            right_frame,
            text="Turn ON",
            command=lambda: self.toggle_relay(relay_num),
            font=('Arial', 11, 'bold'),
            bg=self.COLORS['success'],
            fg=self.COLORS['text_white'],
            activebackground=self.COLORS['success_dark'],
            relief=tk.FLAT,
            cursor='hand2',
            width=12,
            height=2,
            bd=0,
            state=tk.DISABLED
        )
        toggle_btn.pack()
        
        # Store references
        self.relay_cards[relay_num] = {
            'card': card_outer,
            'toggle_btn': toggle_btn,
            'status_badge': status_badge,
            'card_frame': card
        }
        
        return card_outer
        
    def refresh_ports(self):
        """Refresh available COM ports"""
        ports = RelayControllerStandalone.get_available_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.current(0)
    
    def toggle_connection(self):
        """Connect or disconnect from relay board"""
        if self.controller and self.controller.is_connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        """Connect to the relay board"""
        port = self.port_combo.get()
        if not port:
            messagebox.showerror("Error", "Please select a COM port")
            return
        
        try:
            self.controller = RelayControllerStandalone(port)
            self.controller.connect()
            
            # Update UI
            self.status_indicator.config(fg=self.COLORS['success'])
            self.status_text.config(text="Connected")
            self.connect_btn.config(
                text="Disconnect",
                bg=self.COLORS['danger'],
                activebackground=self.COLORS['danger_dark']
            )
            
            # Enable controls
            self.all_on_btn.config(state=tk.NORMAL)
            self.all_off_btn.config(state=tk.NORMAL)
            for i in range(1, 5):
                self.relay_cards[i]['toggle_btn'].config(state=tk.NORMAL)
            
            # Start status updates
            self.status_update_running = True
            threading.Thread(target=self.update_status_loop, daemon=True).start()
            
            messagebox.showinfo("Success", f"Connected to {port}")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
    
    def disconnect(self):
        """Disconnect from relay board"""
        if self.controller:
            self.status_update_running = False
            self.controller.disconnect()
            
            # Update UI
            self.status_indicator.config(fg=self.COLORS['text_light'])
            self.status_text.config(text="Disconnected")
            self.connect_btn.config(
                text="Connect",
                bg=self.COLORS['primary'],
                activebackground=self.COLORS['primary_dark']
            )
            
            # Disable controls
            self.all_on_btn.config(state=tk.DISABLED)
            self.all_off_btn.config(state=tk.DISABLED)
            for i in range(1, 5):
                self.relay_cards[i]['toggle_btn'].config(state=tk.DISABLED)
                self.update_relay_ui(i, False)
    
    def toggle_relay(self, relay_num):
        """Toggle relay on/off"""
        if not self.controller or not self.controller.is_connected:
            messagebox.showerror("Error", "Not connected to relay board")
            return
        
        current_state = self.relay_states.get(relay_num, False)
        if current_state:
            self.turn_relay_off(relay_num)
        else:
            self.turn_relay_on(relay_num)
    
    def turn_relay_on(self, relay_num):
        """Turn on specific relay"""
        if not self.controller or not self.controller.is_connected:
            return
        
        try:
            self.controller.turn_on(relay_num)
            self.relay_states[relay_num] = True
            self.update_relay_ui(relay_num, True)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def turn_relay_off(self, relay_num):
        """Turn off specific relay"""
        if not self.controller or not self.controller.is_connected:
            return
        
        try:
            self.controller.turn_off(relay_num)
            self.relay_states[relay_num] = False
            self.update_relay_ui(relay_num, False)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def turn_all_on(self):
        """Turn on all relays"""
        for i in range(1, 5):
            self.turn_relay_on(i)
    
    def turn_all_off(self):
        """Turn off all relays"""
        for i in range(1, 5):
            self.turn_relay_off(i)
    
    def update_relay_ui(self, relay_num, is_on):
        """Update UI for relay status"""
        card = self.relay_cards[relay_num]
        
        if is_on:
            # ON state
            card['status_badge'].config(
                text="ON",
                bg=self.COLORS['relay_on_bg'],
                fg=self.COLORS['success']
            )
            card['toggle_btn'].config(
                text="Turn OFF",
                bg=self.COLORS['danger'],
                activebackground=self.COLORS['danger_dark']
            )
            # Highlight border
            card['card_frame'].config(highlightbackground=self.COLORS['success'], highlightthickness=2)
        else:
            # OFF state
            card['status_badge'].config(
                text="OFF",
                bg=self.COLORS['relay_off_bg'],
                fg=self.COLORS['danger']
            )
            card['toggle_btn'].config(
                text="Turn ON",
                bg=self.COLORS['success'],
                activebackground=self.COLORS['success_dark']
            )
            # Remove border highlight
            card['card_frame'].config(highlightthickness=0)
    
    def update_status_loop(self):
        """Continuously update relay status"""
        while self.status_update_running:
            if self.controller and self.controller.is_connected:
                try:
                    statuses = self.controller.get_status()
                    for relay_num in range(1, 5):
                        key = f"R{relay_num}"
                        if key in statuses:
                            is_on = statuses[key] == "ON"
                            self.relay_states[relay_num] = is_on
                            self.root.after(0, self.update_relay_ui, relay_num, is_on)
                except Exception:
                    pass
            time.sleep(1.0)
    
    def on_closing(self):
        """Handle window closing"""
        self.status_update_running = False
        if self.controller and self.controller.is_connected:
            self.controller.disconnect()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ModernRelayDashboard(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
