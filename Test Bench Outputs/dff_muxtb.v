`timescale 1ns/1ps



module dff_mux_tb;

	reg clk;
	reg sel;
	reg rst;
	reg a;
	reg b;
	wire out;
dff_mux dff_mux_tb (
	.clk(clk),
	.sel(sel),
	.rst(rst),
	.a(a),
	.b(b),
	.out(out)
);



	integer i;

initial begin
	clk = 0;
	forever begin #5 clk = ~clk;
end
end
initial begin
	#2 // Initial delay
	//======================================================
	// NBAs Test
	//======================================================

$display("----------NON BLOCKING ASSIGNMENT TESTS----------");	// NBA Test for RHS: (sel)? a: b
	sel = 1'b1;
	#2
	sel = 1'b0;
	#2
	rst = 1;
	#2
	rst = 0;
	#2
	#2
	// NBA Test for RHS: (sel)? a: b
	a = 1'b1;
	#2
	a = 1'b0;
	#2
	rst = 1;
	#2
	rst = 0;
	#2
	#2
	// NBA Test for RHS: (sel)? a: b
	b = 1'b0;
	#2
	b = 1'b1;
	#2
	rst = 1;
	#2
	rst = 0;
	#2
	#2
	//======================================================
	//======================================================
	// If Statements Test
	//======================================================

$display("----------IF TESTS----------");	// If Statement Test for IFMEMBERS: ['rst']
	rst = 1'b0;
	#2
	rst = 1'b1;
	#2
	rst = 1;
	#2
	rst = 0;
	#2
	#2
	//======================================================
	//======================================================
	// Logical Test
	//======================================================

$display("----------LOGICAL OPERATOR TESTS----------");	// Logical Test for Member: sel
	sel = 1'b0;
	#2
	sel = 1'b1;
	#2
	rst = 1;
	#2
	rst = 0;
	#2
	#2
	//======================================================
	//======================================================
	// Random Test Loop
	//======================================================

$display("----------FULLY RANDOM TEST LOOP----------");		for (i = 0; i < 20 ; i = i + 1) begin
			sel = {$random} % 2;
			#2;
			rst = {$random} % 2;
			#2;
			a = {$random} % 2;
			#2;
			b = {$random} % 2;
			#2;
		end
$stop;
end
	//======================================================
	// Monitor Block
	//======================================================
	initial begin
		$monitor("Time = %0t out = %b", $time , out);	end

endmodule