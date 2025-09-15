// print_layout.scad
// Optimized print layout for two-piece Alexa-style Pi Voice Assistant Case

// Include the shared modules file
include <shared_modules.scad>

// Main body - upright (solid bottom down)
main_body();

// Top lid - positioned for printing  
translate([case_diameter + 20, 0, 0])
    top_lid();