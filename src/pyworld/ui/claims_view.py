import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from ..models.universe import RegionVisibility

class ClaimsView(ttk.Frame):
    """A view for managing system claims"""
    
    def __init__(self, parent, game_state):
        super().__init__(parent)
        self.game_state = game_state
        
        # Create UI
        self.create_widgets()
        
        # Schedule periodic updates
        self.after(1000, self.update_displays)
    
    def create_widgets(self):
        """Create the claims view widgets"""
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        
        # Left panel - Available Claims
        self.available_frame = ttk.LabelFrame(self, text="Available Claims", padding="10")
        self.available_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Available claims list
        self.available_list = ttk.Treeview(
            self.available_frame,
            columns=('system', 'level', 'duration'),
            show='headings'
        )
        self.available_list.heading('system', text='System')
        self.available_list.heading('level', text='Level')
        self.available_list.heading('duration', text='Duration')
        self.available_list.column('system', width=100)
        self.available_list.column('level', width=50)
        self.available_list.column('duration', width=100)
        self.available_list.pack(fill='both', expand=True)
        
        # Bind selection event
        self.available_list.bind('<<TreeviewSelect>>', self.on_available_select)
        self.available_list.bind('<Button-3>', self.show_available_context_menu)
        
        # Claim button
        self.claim_button = ttk.Button(
            self.available_frame,
            text="Claim Selected System",
            command=self.claim_selected_system
        )
        self.claim_button.pack(pady=10)
        
        # Right panel - Active Claims
        self.active_frame = ttk.LabelFrame(self, text="Active Claims", padding="10")
        self.active_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Active claims list
        self.active_list = ttk.Treeview(
            self.active_frame,
            columns=('system', 'level', 'expires'),
            show='headings'
        )
        self.active_list.heading('system', text='System')
        self.active_list.heading('level', text='Level')
        self.active_list.heading('expires', text='Expires')
        self.active_list.column('system', width=100)
        self.active_list.column('level', width=50)
        self.active_list.column('expires', width=150)
        self.active_list.pack(fill='both', expand=True)
        
        # Bind selection event
        self.active_list.bind('<<TreeviewSelect>>', self.on_active_select)
        self.active_list.bind('<Button-3>', self.show_active_context_menu)
        
        # Bottom panel - Details
        self.details_frame = ttk.LabelFrame(self, text="Claim Details", padding="10")
        self.details_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        
        # Claim details
        self.details_text = tk.Text(self.details_frame, wrap='word', height=5)
        self.details_text.pack(fill='both', expand=True)
        self.details_text.insert('1.0', "Select a claim to view details.")
        self.details_text.config(state='disabled')
        
        # Store selected claim IDs
        self.selected_available_id = None
        self.selected_active_id = None
        
        # Create context menus
        self.create_context_menus()
    
    def create_context_menus(self):
        """Create context menus for claims"""
        # Available claims context menu
        self.available_menu = tk.Menu(self, tearoff=0)
        self.available_menu.add_command(label="Claim System", command=self.claim_selected_system)
        self.available_menu.add_command(label="View Details", command=self.view_available_details)
        
        # Active claims context menu
        self.active_menu = tk.Menu(self, tearoff=0)
        self.active_menu.add_command(label="Send Fleet", command=self.send_fleet_to_claimed)
        self.active_menu.add_command(label="Probe Region", command=self.probe_region)
        self.active_menu.add_command(label="View Details", command=self.view_active_details)
    
    def show_available_context_menu(self, event):
        """Show context menu for available claims"""
        # Select the item under cursor
        item = self.available_list.identify_row(event.y)
        if item:
            self.available_list.selection_set(item)
            self.available_list.focus(item)
            self.on_available_select(None)  # Update details
            self.available_menu.post(event.x_root, event.y_root)
    
    def show_active_context_menu(self, event):
        """Show context menu for active claims"""
        # Select the item under cursor
        item = self.active_list.identify_row(event.y)
        if item:
            self.active_list.selection_set(item)
            self.active_list.focus(item)
            self.on_active_select(None)  # Update details
            self.active_menu.post(event.x_root, event.y_root)
    
    def view_available_details(self):
        """View details of available claim"""
        selection = self.available_list.selection()
        if selection:
            # Already handled by selection event
            pass
    
    def view_active_details(self):
        """View details of active claim"""
        selection = self.active_list.selection()
        if selection:
            # Already handled by selection event
            pass
            
    def send_fleet_to_claimed(self):
        """Send a fleet to the claimed system"""
        selection = self.active_list.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a claimed system to send a fleet to.")
            return
        
        # Get selected claim
        item = self.active_list.item(selection[0])
        system_name = item['values'][0]
        
        # Find the claim
        claim = None
        for c in self.game_state.get_active_claims():
            if c.region.name == system_name:
                claim = c
                break
        
        if not claim:
            messagebox.showerror("Error", "Selected claim not found.")
            return
        
        # Get current fleet
        current_fleet = self.game_state.get_current_fleet()
        if not current_fleet:
            messagebox.showerror("No Fleet", "You need to select a fleet first.")
            return
            
        # Check if fleet is already traveling
        if current_fleet.is_traveling:
            messagebox.showerror("Fleet Traveling", 
                                "This fleet is already traveling. Please wait until it arrives.")
            return
        
        # Calculate travel time based on system level
        travel_hours = 1/60 * claim.region.level  # Level 1 = 1 minute, Level 2 = 2 minutes, etc.
        
        # Send fleet to claimed system
        try:
            current_fleet.travel_to(claim.region, travel_hours)
            messagebox.showinfo(
                "Fleet Dispatched",
                f"Your fleet has been dispatched to {system_name}. " +
                f"Estimated arrival in {travel_hours * 60:.0f} minutes."
            )
        except Exception as e:
            messagebox.showerror("Travel Failed", str(e))
    
    def probe_region(self):
        """Start probing the selected region"""
        selection = self.active_list.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a claimed region to probe.")
            return
        
        # Get selected claim
        item = self.active_list.item(selection[0])
        system_name = item['values'][0]
        
        # Find the claim
        claim = None
        for c in self.game_state.get_active_claims():
            if c.region.name == system_name:
                claim = c
                break
        
        if not claim:
            messagebox.showerror("Error", "Selected claim not found.")
            return
        
        # Get current fleet
        current_fleet = self.game_state.get_current_fleet()
        if not current_fleet:
            messagebox.showerror("No Fleet", "You need to select a fleet first.")
            return
            
        # Check if fleet is already traveling
        if current_fleet.is_traveling:
            messagebox.showerror("Fleet Traveling", 
                                "This fleet is already traveling. Please wait until it arrives.")
            return
            
        # Check if fleet is already probing
        if current_fleet.is_probing:
            messagebox.showerror("Fleet Probing", 
                                "This fleet is already probing. Please wait until it completes.")
            return
            
        # Check if fleet is in the correct region
        if current_fleet.current_region != claim.region:
            messagebox.showerror("Wrong Region", 
                                f"Your fleet must be in {claim.region.name} to probe it. Travel there first.")
            return
        
        # Start probing
        try:
            current_fleet.start_probing(claim.region)
            probe_hours = 0.5 * claim.region.level
            messagebox.showinfo(
                "Probing Started",
                f"Your fleet has started probing {system_name}. " +
                f"Estimated completion in {probe_hours:.1f} hours."
            )
        except Exception as e:
            messagebox.showerror("Probing Failed", str(e))
    
    def on_available_select(self, event):
        """Handle selection in the available claims list"""
        selection = self.available_list.selection()
        if selection:
            # Clear active list selection
            self.active_list.selection_remove(*self.active_list.selection())
            
            # Get selected item
            item = self.available_list.item(selection[0])
            system_name = item['values'][0]
            self.selected_available_id = selection[0]
            self.selected_active_id = None
            
            # Find the claim
            claim = None
            for c in self.game_state.get_available_claims():
                if c.region.name == system_name:
                    claim = c
                    break
            
            # Update details
            if claim:
                self.update_details(claim)
    
    def on_active_select(self, event):
        """Handle selection in the active claims list"""
        selection = self.active_list.selection()
        if selection:
            # Clear available list selection
            self.available_list.selection_remove(*self.available_list.selection())
            
            # Get selected item
            item = self.active_list.item(selection[0])
            system_name = item['values'][0]
            self.selected_active_id = selection[0]
            self.selected_available_id = None
            
            # Find the claim
            claim = None
            for c in self.game_state.get_active_claims():
                if c.region.name == system_name:
                    claim = c
                    break
            
            # Update details
            if claim:
                self.update_details(claim)
    
    def update_details(self, claim):
        """Update the details panel with information about the selected claim"""
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', tk.END)
        
        if hasattr(claim, 'is_active') and claim.is_active():
            # Active claim
            time_left = claim.time_remaining()
            hours = time_left.total_seconds() / 3600
            details = (
                f"Region: {claim.region.name}\n"
                f"Level: {claim.region.level}\n"
                f"Corporation: {claim.corporation}\n"
                f"Expires in: {hours:.1f} hours\n"
                f"Resource deposits: {len(claim.region.deposits)}"
            )
        else:
            # Available claim
            details = (
                f"Region: {claim.region.name}\n"
                f"Level: {claim.region.level}\n"
                f"Duration: {claim.duration.total_seconds() / 3600:.1f} hours\n"
                f"Resource deposits: {len(claim.region.deposits)}"
            )
        
        self.details_text.insert('1.0', details)
        self.details_text.config(state='disabled')
    
    def update_displays(self):
        """Update the displays with current information"""
        # Store current selections
        avail_selected = self.available_list.selection()
        active_selected = self.active_list.selection()
        
        # Remember the selected region names for restoring selection
        selected_available_region = None
        if avail_selected:
            item = self.available_list.item(avail_selected[0])
            selected_available_region = item['values'][0]
            
        selected_active_region = None
        if active_selected:
            item = self.active_list.item(active_selected[0])
            selected_active_region = item['values'][0]
        
        # Clear existing items
        for item in self.available_list.get_children():
            self.available_list.delete(item)
        
        for item in self.active_list.get_children():
            self.active_list.delete(item)
        
        # Add available claims
        available_id_to_select = None
        for claim in self.game_state.get_available_claims():
            item_id = self.available_list.insert('', 'end', values=(
                claim.region.name,
                claim.region.level,
                f"{claim.duration.total_seconds() / 3600:.1f} hours"
            ))
            # Check if this was previously selected
            if selected_available_region and claim.region.name == selected_available_region:
                available_id_to_select = item_id
        
        # Add active claims
        active_id_to_select = None
        for claim in self.game_state.get_active_claims():
            now = datetime.now()
            time_left = claim.expiry - now
            if time_left.total_seconds() <= 0:
                continue  # Skip expired claims
                
            item_id = self.active_list.insert('', 'end', values=(
                claim.region.name,
                claim.region.level,
                f"{time_left.total_seconds() / 3600:.1f} hours left"
            ))
            # Check if this was previously selected
            if selected_active_region and claim.region.name == selected_active_region:
                active_id_to_select = item_id
        
        # Restore selections
        if available_id_to_select:
            self.available_list.selection_set(available_id_to_select)
            self.available_list.focus(available_id_to_select)
        elif active_id_to_select:
            self.active_list.selection_set(active_id_to_select)
            self.active_list.focus(active_id_to_select)
        
        # Schedule next update
        self.after(1000, self.update_displays)
    
    def claim_selected_system(self):
        """Claim the selected system"""
        selection = self.available_list.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a system to claim.")
            return
        
        # Get selected claim
        item = self.available_list.item(selection[0])
        system_name = item['values'][0]
        
        # Find the claim
        claim = None
        for c in self.game_state.get_available_claims():
            if c.region.name == system_name:
                claim = c
                break
        
        if not claim:
            messagebox.showerror("Error", "Selected claim not found.")
            return
        
        # Attempt to claim the system
        try:
            # Save selection information before modifying the list
            selected_region_name = system_name
            
            # Claim the system (this modifies the available_claims list)
            self.game_state.claim_system(claim)
            
            # Show success message
            messagebox.showinfo(
                "Claim Successful",
                f"You have successfully claimed {system_name} for {claim.duration.total_seconds() / 3600:.1f} hours."
            )
            
            # The selection is no longer valid since the item has been removed
            # No need to remove the selection, just set our tracking variables
            self.selected_available_id = None
            
            # Update display immediately to show the changes
            self.update_displays()
            
            # Find and select the newly claimed region in the active list
            for item_id in self.active_list.get_children():
                item = self.active_list.item(item_id)
                if item['values'][0] == selected_region_name:
                    self.active_list.selection_set(item_id)
                    self.active_list.focus(item_id)
                    self.selected_active_id = item_id
                    
                    # Find the claim again in the active claims
                    for c in self.game_state.get_active_claims():
                        if c.region.name == selected_region_name:
                            # Update details for the newly claimed region
                            self.update_details(c)
                            break
                    break
            
        except Exception as e:
            # More detailed error message
            import traceback
            error_message = f"Error: {str(e)}\n\n{traceback.format_exc()}"
            print(error_message)  # Print to console for debugging
            messagebox.showerror("Claim Failed", str(e)) 