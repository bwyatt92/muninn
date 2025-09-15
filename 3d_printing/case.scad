// Alexa-style Raspberry Pi 5 Voice Assistant Case
// Includes: Pi 5, Voice Bonnet, Speaker, NeoPixel strip, Active Cooler

// Main dimensions
case_diameter = 110;
case_height = 85;
wall_thickness = 2.5;
bottom_thickness = 3;

// Component dimensions
pi_width = 85;
pi_length = 56;
pi_thickness = 5;
voice_bonnet_thickness = 20; // includes components
speaker_diameter = 60;
speaker_height = 25;
cooler_height = 30;

// LED strip parameters
led_strip_width = 10;
led_strip_thickness = 3;
led_window_width = 12;
led_window_height = 8;

// Feature toggles
show_components = false; // Set to true to see component placement
exploded_view = false;   // Set to true for exploded assembly view

module main_body() {
    difference() {
        // Main cylinder
        cylinder(h=case_height, d=case_diameter, $fn=80);
        
        // Hollow interior
        translate([0, 0, bottom_thickness])
            cylinder(h=case_height, d=case_diameter-2*wall_thickness, $fn=80);
        
        // Speaker grille (bottom)
        translate([0, 0, -0.1]) {
            // Central hole for main sound
            cylinder(h=bottom_thickness+0.2, d=40, $fn=60);
            
            // Ring of smaller holes for better sound distribution
            for(i = [0:11]) {
                rotate([0, 0, i*30])
                    translate([25, 0, 0])
                        cylinder(h=bottom_thickness+0.2, d=6, $fn=20);
            }
            
            // Outer ring
            for(i = [0:23]) {
                rotate([0, 0, i*15])
                    translate([35, 0, 0])
                        cylinder(h=bottom_thickness+0.2, d=4, $fn=16);
            }
        }
        
        // Microphone slits (top area)
        for(i = [0:5]) {
            rotate([0, 0, i*60])
                translate([case_diameter/2 - wall_thickness/2, 0, case_height - 15])
                    rotate([0, 90, 0])
                        hull() {
                            cylinder(h=wall_thickness+0.2, d=2, $fn=16);
                            translate([0, 0, 0])
                                translate([0, 8, 0])
                                    cylinder(h=wall_thickness+0.2, d=2, $fn=16);
                        }
        }
        
        // LED light diffusion windows
        translate([0, 0, case_height/2]) {
            for(i = [0:11]) {
                rotate([0, 0, i*30])
                    translate([case_diameter/2 - wall_thickness/2, 0, 0])
                        cube([wall_thickness+0.2, led_window_width, led_window_height], center=true);
            }
        }
        
        // Ventilation holes for active cooler
        for(i = [0:7]) {
            rotate([0, 0, i*45 + 22.5]) // Offset from LED windows
                translate([case_diameter/2 - wall_thickness/2, 0, 25])
                    rotate([0, 90, 0])
                        cylinder(h=wall_thickness+0.2, d=8, $fn=20);
        }
        
        // Cable management hole
        translate([case_diameter/2 - wall_thickness/2, 0, 10])
            rotate([0, 90, 0])
                cylinder(h=wall_thickness+0.2, d=12, $fn=20);
    }
    
    // Internal support posts for Pi mounting
    pi_support_height = bottom_thickness + 5;
    
    // Pi mounting posts (standard Pi mounting holes)
    pi_hole_spacing_x = 58;
    pi_hole_spacing_y = 49;
    
    for(x = [-1, 1], y = [-1, 1]) {
        translate([x * pi_hole_spacing_x/2, y * pi_hole_spacing_y/2, 0]) {
            difference() {
                cylinder(h=pi_support_height, d=6, $fn=20);
                cylinder(h=pi_support_height+0.1, d=2.5, $fn=16); // M2.5 screw hole
            }
        }
    }
    
    // Central support column for stability
    translate([0, 0, 0]) {
        difference() {
            cylinder(h=pi_support_height-2, d=12, $fn=20);
            cylinder(h=pi_support_height, d=6, $fn=16);
        }
    }
    
    // LED strip mounting channels
    translate([0, 0, case_height/2]) {
        difference() {
            cylinder(h=led_strip_thickness+2, d=case_diameter-2*wall_thickness-2, $fn=80);
            cylinder(h=led_strip_thickness+3, d=case_diameter-2*wall_thickness-2-led_strip_width-2, $fn=80);
        }
    }
}

module top_lid() {
    translate([0, 0, exploded_view ? case_height + 20 : 0]) {
        difference() {
            union() {
                // Main lid
                cylinder(h=3, d=case_diameter, $fn=80);
                
                // Lip to fit into case
                translate([0, 0, -8])
                    cylinder(h=8, d=case_diameter-2*wall_thickness-0.4, $fn=80);
            }
            
            // Microphone holes
            for(i = [0:1]) {
                rotate([0, 0, i*180])
                    translate([15, 0, -0.1])
                        cylinder(h=4, d=8, $fn=20);
            }
            
            // Status LED hole (center)
            cylinder(h=4, d=5, $fn=20);
            
            // Decorative ring pattern
            for(i = [0:35]) {
                rotate([0, 0, i*10])
                    translate([35, 0, -0.1])
                        cylinder(h=1.5, d=2, $fn=12);
            }
        }
    }
}

// Component visualization (for reference)
module components() {
    if(show_components) {
        color("green", 0.7) {
            // Raspberry Pi 5
            translate([-pi_length/2, -pi_width/2, bottom_thickness + 5])
                cube([pi_length, pi_width, pi_thickness]);
            
            // Voice Bonnet
            translate([-pi_length/2, -pi_width/2, bottom_thickness + 5 + pi_thickness])
                cube([pi_length, pi_width, voice_bonnet_thickness]);
        }
        
        color("black", 0.7) {
            // Speaker
            translate([0, 0, -(speaker_height-bottom_thickness)])
                cylinder(h=speaker_height, d=speaker_diameter, $fn=40);
        }
        
        color("blue", 0.7) {
            // Active cooler
            translate([15, 15, bottom_thickness + 5 + pi_thickness])
                cube([25, 25, cooler_height]);
        }
        
        color("red", 0.8) {
            // LED strip (simplified as ring)
            translate([0, 0, case_height/2])
                difference() {
                    cylinder(h=led_strip_thickness, d=case_diameter-2*wall_thickness-4, $fn=80);
                    cylinder(h=led_strip_thickness+0.1, d=case_diameter-2*wall_thickness-4-led_strip_width, $fn=80);
                }
        }
    }
}

module assembly_notes() {
    // Assembly instruction locations
    if(show_components) {
        color("yellow") {
            // Cable routing indicators
            translate([case_diameter/2-5, 0, 15])
                cube([2, 2, 20]);
        }
    }
}

// Generate the parts
main_body();
top_lid();
components();
assembly_notes();

// Print layout (uncomment for printing preparation)
/*
translate([case_diameter + 10, 0, 0]) top_lid();
translate([0, case_diameter + 10, 0]) 
    rotate([0, 180, 0]) 
        translate([0, 0, -case_height]) 
            main_body();
*/