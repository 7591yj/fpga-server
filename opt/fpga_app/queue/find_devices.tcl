open_hw_manager
connect_hw_server -url localhost:3121
refresh_hw_server
open_hw_target
refresh_hw_target
set fh [open "targets.txt" "w"]
foreach t [get_hw_targets] {
    puts $fh $t
}
close $fh
