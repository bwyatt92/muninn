// assembly_view.scad
// Complete three-piece assembly view for Alexa-style Pi Voice Assistant Case

// Include the shared modules file
include <shared_modules.scad>

// Show complete assembly
main_body();
bottom_lid();
top_lid();

// Show components (set show_components = true in shared_modules.scad to see them)
components();