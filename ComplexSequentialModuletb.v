`timescale 1ns/1ps



module ComplexSequentialModule_tb;

	reg [7:0] vector_in;
	reg clk;
	reg reset;
	reg [3:0] case_test;
	reg [3:0] case_test2;
	reg [6:0] test3;
	reg [2:0] test4;
	reg [2:0] test5;
	wire [7:0] vector_out;
	wire [7:0] test_out;
	reg test_in;
	wire logic_out;
	wire logic_out2;
	wire logic_out3;
ComplexSequentialModule ComplexSequentialModule_tb (
	.vector_in(vector_in),
	.clk(clk),
	.reset(reset),
	.case_test(case_test),
	.case_test2(case_test2),
	.test3(test3),
	.test4(test4),
	.test5(test5),
	.vector_out(vector_out),
	.test_out(test_out),
	.test_in(test_in),
	.logic_out(logic_out),
	.logic_out2(logic_out2),
	.logic_out3(logic_out3)
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
	// BAs Test
	//======================================================

$display("----------BLOCKING ASSIGNMENT TESTS----------");	// BA Test for RHS: vector_in
	vector_in = 8'b11000000;
	#2
	vector_in = 8'b11001100;
	#2
	vector_in = 8'b11000011;
	#2
	vector_in = 8'b01010001;
	#2
	vector_in = 8'b11001111;
	#2
	reset = 1;
	#2
	reset = 0;
	#2
	#2
	// BA Test for RHS: test_in
	test_in = 1'b1;
	#2
	test_in = 1'b0;
	#2
	reset = 1;
	#2
	reset = 0;
	#2
	#2
	//======================================================
	//======================================================
	// NBAs Test
	//======================================================

$display("----------NON BLOCKING ASSIGNMENT TESTS----------");	// NBA Test for RHS: vector_in + 8'b00000001
	vector_in = 8'b00000001;
	#2
	vector_in = 8'b00011110;
	#2
	vector_in = 8'b10011001;
	#2
	vector_in = 8'b11010101;
	#2
	vector_in = 8'b10110001;
	#2
	reset = 1;
	#2
	reset = 0;
	#2
	#2
	//======================================================
	//======================================================
	// Random and Specific Case Test
	//======================================================

$display("----------RANDOM CASE TESTS----------");	// Case Test for CASEMEMBERS: ['case_test']
	case_test = 4'b0101;
	#2;
	case_test = 4'b1001;
	#2;
	case_test = 4'b1110;
	#2;
	case_test = 4'b1010;
	#2;
	case_test = 4'b1010;
	#2;
	reset = 1;
	#2
	reset = 0;
	#2
	#2;

$display("----------SPECIFIC CASE TESTS----------");	// Case Attempt Test for OWNER: case_test, CASE: 4'b0000
	case_test = 4'b0000;
	#2;
	reset = 1;
	#2
	reset = 0;
	#2
	#2;
	// Case Attempt Test for OWNER: case_test, CASE: 4'b0001
	case_test = 4'b0001;
	#2;
	reset = 1;
	#2
	reset = 0;
	#2
	#2;
	// Case Attempt Test for OWNER: case_test, CASE: 4'b0010
	case_test = 4'b0010;
	#2;
	reset = 1;
	#2
	reset = 0;
	#2
	#2;
	//======================================================
	//======================================================
	// If Statements Test
	//======================================================

$display("----------IF TESTS----------");	// If Statement Test for IFMEMBERS: ['reset']
	reset = 1'b0;
	#2
	reset = 1'b1;
	#2
	reset = 1;
	#2
	reset = 0;
	#2
	#2
	// If Statement Test for IFMEMBERS: ['vector_in']
	vector_in = 8'b10010110;
	#2
	vector_in = 8'b10110001;
	#2
	vector_in = 8'b00011011;
	#2
	vector_in = 8'b01010000;
	#2
	vector_in = 8'b10000011;
	#2
	reset = 1;
	#2
	reset = 0;
	#2
	#2
	//======================================================
	//======================================================
	// Logical Test
	//======================================================

$display("----------LOGICAL OPERATOR TESTS----------");	// Logical Test for Member: vector_in
	vector_in = 8'b01111010;
	#2
	vector_in = 8'b10001001;
	#2
	vector_in = 8'b01000000;
	#2
	vector_in = 8'b10101101;
	#2
	vector_in = 8'b00010011;
	#2
	reset = 1;
	#2
	reset = 0;
	#2
	#2
	//======================================================
	//======================================================
	// Random Test Loop
	//======================================================

$display("----------FULLY RANDOM TEST LOOP----------");		for (i = 0; i < 100 ; i = i + 1) begin
			vector_in = {$random} % 256;
			#2;
			reset = {$random} % 2;
			#2;
			case_test = {$random} % 16;
			#2;
			case_test2 = {$random} % 16;
			#2;
			test3 = {$random} % 128;
			#2;
			test4 = {$random} % 8;
			#2;
			test5 = {$random} % 8;
			#2;
			test_in = {$random} % 2;
			#2;
		end
$stop;
end
	//======================================================
	// Monitor Block
	//======================================================
	initial begin
		$monitor("Time = %0t vector_out = %b test_out = %b logic_out = %b logic_out2 = %b logic_out3 = %b", $time , vector_out, test_out, logic_out, logic_out2, logic_out3);	end

endmodule