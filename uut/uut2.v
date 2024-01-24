module Mux4to1(SEL,A,B,C,D,F);
    input [1:0] SEL;
    input A,B,C,D;
    output reg F;

    always @(SEL or A or B or C or D)
    begin
    case(SEL)
    2'b00: F = A;
    2'b01: F = B;
    2'b10: F = C;
    2'b11: F = D;
    endcase
    end

endmodule