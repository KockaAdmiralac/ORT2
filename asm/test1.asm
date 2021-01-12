        LD #0x1000   ; Učitava se 1000h u akumulator               N = 0, Z = 0, C = 0, V = 0
        ST 2000h     ; Upisuje se 1000h na adresu 2000h            N = 0, Z = 0, C = 0, V = 0
        ADD (2000h)  ; Dodaje se 3000h na akumulator, A = 2000h    N = 0, Z = 0, C = 0, V = 0
        PUSH         ; Gura se 2000h na stek                       N = 0, Z = 0, C = 0, V = 0
        ADD #-1      ; Smanjuje akumulator za 1                    N = 0, Z = 0, C = 1, V = 0
        BNNG -6      ; Skače na prethodnu instrukciju četiri puta  N = ?, Z = ?, C = 0, V = 0
        JSR funk     ; Skače na potprogram na labeli funk          N = 1, Z = 0, C = 0, V = 0
        INC R1       ; Inkrementira R1, R1 = 1
curr:   LD (R1)      ; U akumulator učitava podatak na adresi 1, A = (IVTP + 1)
        ADD (R1)+    ; U akumulator dodaje podatak na adresi 1, A = 2 * (IVTP + 1), R1 = 2
        OR (R1)-     ; Radi logičko ILI sa podatkom na adresi 2, R1 = 1
        HALT         ; Zaustavlja program
        ST #3        ; Isključuje procesor (nije validna instrukcija a sledeća se prepozna kao HALT)
funk:   LD #1000h    ; Učitava se 1000h u akumulator
        ROR          ; Rotira se akumulator udesno
        BGREU -0b11  ; Vraća se na rotaciju dok se dešava prenos
        RTS          ; Vraća se na mesto pozivanja
intr0:  LD #0b1111
        ST R2
intr1:  LD #-23
        ST R3
intr2:  LD #0x11
        ST R4
intr3:  RTI
