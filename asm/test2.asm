        LD #1010h   ; Formiranje niske u memoriji
        ST 2000h
        LD #202h
        PUSH        ; Guranje na stek
        ST 2002h
        LD #111h
        ST 2004h
        LD #0
        JLEQ pop    ; Skakanje jer je Z = 1
        ST 2006h
pop:    POP         ; Vraćanje sa steka
        BGRT 1      ; Preskakanje HALT
        HALT
        RORC
        LD #2211h
        STRFIND #2000h
        HALT
