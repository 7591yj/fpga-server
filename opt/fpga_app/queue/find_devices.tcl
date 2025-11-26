# Connect to local hardware server and open target
open_hw_manager
connect_hw_server -url localhost:3121
open_hw_target
refresh_hw_target

# Get both devices and targets
set devices [get_hw_devices]
set targets [get_hw_targets]

# Open file for writing JSON
set fh [open "targets.json" "w"]
puts $fh {[}
set sep ""

# Iterate over targets and their devices
foreach t $targets {
    set transport     [get_property PARAM.TYPE $t]
    set product       [get_property PARAM.DEVICE $t]
    set serial_number [get_property UID $t]

    # Retrieve devices under this target
    set devs [get_hw_devices -of_objects $t]
    foreach d $devs {
        set device_name [get_property PART $d]
        set device_id   [get_property IDCODE_HEX $d]

        puts $fh "$sep{"
        puts $fh "  \"target\": \"[string trim $t]\","
        puts $fh "  \"device\": \"[string trim $d]\","
        puts $fh "  \"device_name\": \"[string trim $device_name]\","
        puts $fh "  \"device_id\": \"[string trim $device_id]\","
        puts $fh "  \"transport_type\": \"[string trim $transport]\","
        puts $fh "  \"product_name\": \"[string trim $product]\","
        puts $fh "  \"serial_number\": \"[string trim $serial_number]\""
        puts $fh "}"
        set sep ","
    }
}

puts $fh {]}
close $fh

puts "Device information exported to targets.json"
