set bitfile [lindex $argv 0]
set target_serial [lindex $argv 1]

open_hw_manager
connect_hw_server -url localhost:3121
set targets [get_hw_targets]

set found_device ""

foreach t $targets {
    open_hw_target $t
    refresh_hw_target
    set serial_number [get_property UID $t]
    if {$serial_number eq $target_serial} {
        set devs [get_hw_devices -of_objects $t]
        if {[llength $devs] > 0} {
            set found_device [lindex $devs 0]
        }
        break
    }
    close_hw_target $t
}

if {$found_device eq ""} {
    puts "Error: target device with serial number $target_serial not found"
    exit 1
}

current_hw_device $found_device
refresh_hw_device -update_hw_probes false [current_hw_device]
set_property PROGRAM.FILE $bitfile [current_hw_device]
program_hw_devices [current_hw_device]

close_hw_target
disconnect_hw_server
exit
