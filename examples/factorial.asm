;################################################################################
;####	Fisier Test 2 - Factorial
;################################################################################
.data
.code
	jmp	START	; salt la start cod
;--------------------------------------------------------------------------------
; Zona Proceduri
;--------------------------------------------------------------------------------
;--------------------------------------------------------------------------------
; Nume		: Functia factorial
; Autori	: Basca Cosmin , Talos Mihai
; Despre	: functie de calcul factorial pana la 8 - demo
; Parametrii	: R1 <- numarul
; Rezultat	: R2 <- (numarul)!
;--------------------------------------------------------------------------------
FACT:
	cmp	r1,0		; test caz initial
	beq	FACT_INIT
	cmp	r1,1
	beq	FACT_INIT
				; calcul factorial

	mov	r3,r1
	dec	r1
	push	r3
	call	FACT		; (k-1)!
	pop	r3
	mov	r4,r2
	call	MUL		; k*(k-1)!
	mov	r2,r6		; scrie rezultatul
	jmp	FACT_SF

FACT_INIT:
	mov	r2,1
FACT_SF:
	ret
;--------------------------------------------------------------------------------
;--------------------------------------------------------------------------------
; Nume		: Functia inmultire
; Autori	: Basca Cosmin , Talos Mihai
; Despre	: functie ce inmulteste 2 numere
; Parametrii	: R3 <- numarul 1  R4 <- numarul 2
; Rezultat	: R6 <- n1*n2
; Obs		: Pentru un rezultat corect produsul operanzilor nu trebuie sa
;		  faca depasire pe 16 biti
;--------------------------------------------------------------------------------
MUL:
	push	r5
	mov	r6,0
	cmp	r4,1
	beq	MUL_SAME
	cmp	r4,0
	beq	MUL_0
	mov	r5,0
	mov	r5,r4
MUL_REP:add	r6,r3
	dec	r5
	cmp	r5,0
	bne	MUL_REP
	jmp	MUL_SF
MUL_SAME:
	mov	r6,r3
	jmp	MUL_SF
MUL_0:	mov	r6,0
MUL_SF:
	pop	r5
	ret
;--------------------------------------------------------------------------------
;--------------------------------------------------------------------------------
; Sfarsit Zona Proceduri
;--------------------------------------------------------------------------------
START:
	add	r1,        6	; 8 = numarul maxim care poate fi calculat
	call	FACT
	END