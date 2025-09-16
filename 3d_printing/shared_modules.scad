// shared_modules.scad
// Two-piece Alexa-style Pi Voice Assistant Case
// Main Body with solid bottom + Top Lid

// Main dimensions - smaller case
case_diameter = 110;
case_height = 55;  // Reduced height since no bottom compartment
wall_thickness = 2.5;
bottom_thickness = 5;  // Thicker solid bottom
lid_thickness = 3;

// Component dimensions
pi_width = 85;
pi_length = 56;
pi_thickness = 5;
voice_bonnet_thickness = 20;
speaker_diameter = 60;
speaker_height = 25;
cooler_height = 30;

// LED strip parameters
led_strip_width = 10;
led_strip_thickness = 3;
led_channel_depth = 4;

// Text parameters for name cutouts
text_height = 4;
text_depth = wall_thickness + 0.2;
text_size = 6;

// Feature toggles
show_components = false;

// Function to create name cutouts
module create_name_cutout(name) {
    linear_extrude(height=text_depth)
        text(name, size=text_size, halign="center", valign="center", font="Liberation Sans:style=Bold");
}

module main_body() {
    echo("=== SIMPLIFIED MAIN BODY ===");
    echo("Case height:", case_height);
    echo("Bottom thickness:", bottom_thickness);
    echo("Internal height:", case_height - bottom_thickness - lid_thickness);
    
    difference() {
        // Main cylinder with solid bottom
        cylinder(h=case_height, d=case_diameter, $fn=80);
        
        // Hollow interior (starts from bottom thickness, not from 0)
        translate([0, 0, bottom_thickness])
            cylinder(h=case_height-bottom_thickness-lid_thickness, d=case_diameter-2*wall_thickness, $fn=80);
        
        // Top lid recess
        translate([0, 0, case_height-lid_thickness])
            cylinder(h=lid_thickness+0.1, d=case_diameter-wall_thickness, $fn=80);
        
        // Solid bottom - no holes needed
        // Bottom is now completely solid for structural strength
        
        // LED name cutouts (positioned in middle height) - extended for proper through-holes
        translate([0, 0, case_height * 0.5]) {
            names = ["CARRIE", "CASSIE", "SCOTT", "BEAU", "LIZZIE", "JEAN", "NICK", "DAKOTA", "BEA", "CHARLIE", "ALLIE", "LUKE", "LYRA", "TUI", "SEVRO", "DEAMBER", "CARYL"];
            // 17 names evenly spaced around the circle (approximately 21.18° apart)
            for(n = [0:16]) {
                rotate([0, 0, n * (360/17)])
                    translate([case_diameter/2 - wall_thickness - 1, 0, 0])  // Start outside the wall
                        rotate([0, 90, 0])
                            linear_extrude(height=wall_thickness + 2)  // Extend beyond both sides
                                text(names[n], size=text_size, halign="center", valign="center", font="Liberation Sans:style=Bold");
            }
        }
        
        // Microphone slits (top area) - REMOVED - these were the oval holes you're seeing
        
        // Power cable access hole - extended for proper through-hole visualization
        rotate([0, 0, 8 * 24])  // Position at BEA's location (8th name * 24° = 192°)
            translate([case_diameter/2 - wall_thickness - 1, 0, bottom_thickness + 8])  // Start outside wall
                rotate([0, 90, 0])
                    hull() {
                        // Create oval shape for USB-C connector - extended through wall
                        translate([0, -6, 0])
                            cylinder(h=wall_thickness+2, d=12, $fn=20);
                        translate([0, 6, 0])
                            cylinder(h=wall_thickness+2, d=12, $fn=20);
                    }
    }
    
    // Pi mounting posts directly on solid bottom - back to center position
    pi_hole_spacing_x = 58;
    pi_hole_spacing_y = 49;
    post_height = 8;
    
    for(x = [-1, 1], y = [-1, 1]) {
        translate([x * pi_hole_spacing_x/2, y * pi_hole_spacing_y/2, bottom_thickness]) {
            difference() {
                cylinder(h=post_height, d=6, $fn=20);
                cylinder(h=post_height+0.1, d=2.5, $fn=16); // M2.5 screw hole
            }
        }
    }
    
    // LED strip mounting channel - positioned just below lid recess to avoid name interference
    translate([0, 0, case_height - lid_thickness - led_channel_depth - 2]) {
        difference() {
            cylinder(h=led_channel_depth, d=case_diameter-2*wall_thickness-4, $fn=80);
            cylinder(h=led_channel_depth+0.1, d=case_diameter-2*wall_thickness-4-led_strip_width, $fn=80);
        }
    }
}

module top_lid() {
    difference() {
        union() {
            // Main top plate  
            cylinder(h=lid_thickness, d=case_diameter, $fn=80);
            
            // Lip to fit into main body
            translate([0, 0, -5])
                cylinder(h=5, d=case_diameter-wall_thickness-0.2, $fn=80);
        }
        
        // Speaker grille holes - each as individual difference operation like the names
        // Center hole
        translate([0, 0, -2])
            cylinder(h=lid_thickness + 4, d=10, $fn=30);
        
        // Inner ring of holes
        for(i = [0:7]) {
            rotate([0, 0, i*45])
                translate([12, 0, -2])
                    cylinder(h=lid_thickness + 4, d=4, $fn=16);
        }
        
        // Middle ring of holes  
        for(i = [0:11]) {
            rotate([0, 0, i*30])
                translate([20, 0, -2])
                    cylinder(h=lid_thickness + 4, d=5, $fn=20);
        }
        
        // Outer ring of holes
        for(i = [0:15]) {
            rotate([0, 0, i*22.5])
                translate([28, 0, -2])
                    cylinder(h=lid_thickness + 4, d=4, $fn=16);
        }
        
        // Outermost ring of holes
        for(i = [0:19]) {
            rotate([0, 0, i*18])
                translate([35, 0, -2])
                    cylinder(h=lid_thickness + 4, d=3, $fn=12);
        }
        
        // Microphone holes for Voice Bonnet - moved outside speaker grille area
        for(i = [0:1]) {
            rotate([0, 0, i*180])
                translate([45, 0, -0.1])  // Moved from 15mm to 45mm radius
                    cylinder(h=lid_thickness+0.2, d=8, $fn=20);
        }
        
        // Decorative ring pattern - removed to avoid overlap
        // (The speaker grille provides sufficient visual interest)
    }
}

// Component visualization
module components() {
    if(show_components) {
        color("green", 0.7) {
            // Raspberry Pi 5 on bottom - back to center position
            translate([-pi_length/2, -pi_width/2, bottom_thickness + 8])
                cube([pi_length, pi_width, pi_thickness]);
            
            // Voice Bonnet
            translate([-pi_length/2, -pi_width/2, bottom_thickness + 8 + pi_thickness])
                cube([pi_length, pi_width, voice_bonnet_thickness]);
        }
        
        color("black", 0.7) {
            // Speaker (now positioned to project up through top lid)
            translate([0, 0, case_height - lid_thickness - speaker_height])
                cylinder(h=speaker_height, d=speaker_diameter, $fn=40);
        }
        
        color("blue", 0.7) {
            // Active cooler
            translate([15, 15, bottom_thickness + 8 + pi_thickness])
                cube([25, 25, cooler_height]);
        }
        
        color("red", 0.8) {
            // LED strip in channel
            translate([0, 0, case_height * 0.5 - led_strip_thickness/2])
                difference() {
                    cylinder(h=led_strip_thickness, d=case_diameter-2*wall_thickness-6, $fn=80);
                    cylinder(h=led_strip_thickness+0.1, d=case_diameter-2*wall_thickness-6-led_strip_width, $fn=80);
                }
        }
    }
}