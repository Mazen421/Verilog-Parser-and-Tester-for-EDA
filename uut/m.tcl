vlib work
vlog -sv -covercell +cover work uut2.v Mux4to1tb.v
vsim work.Mux4to1_tb -coverage -novopt
add wave *
run -all
coverage save mod.ucdb -onexit
