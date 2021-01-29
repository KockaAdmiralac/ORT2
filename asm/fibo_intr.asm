start: LD #0x100
ST R1
LD #0x102
ST R2
LD #1
ST (R1)
ST (R2)
BNNG -2

intr0: LD (R1)+
ADD (R2)+
ST (R2)
RTI
