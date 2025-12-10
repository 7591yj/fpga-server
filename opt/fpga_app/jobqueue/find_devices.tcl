open_hw_manager
connect_hw_server -url localhost:3121
set targets [get_hw_targets]
foreach t $targets {
    open_hw_target $t
    refresh_hw_target
    set transport     [get_property PARAM.TYPE $t]
    set product       [get_property PARAM.DEVICE $t]
    set serial_number [get_property UID $t]
    set devs [get_hw_devices -of_objects $t]
    foreach d $devs {
        set device_name [get_property PART $d]
        set device_id   [get_property IDCODE_HEX $d]

        puts "[string trim $device_name]|[string trim $device_id]|[string trim $transport]|[string trim $product]|[string trim $serial_number]"
    }
    close_hw_target $t
}
close_hw_target
disconnect_hw_server
exit
