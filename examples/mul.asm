;################################################################################
;####	Fisier Test 3 - MUL
;################################################################################
.data
.code
	jmp	START	
MUL:
	push	r5	
	xor	r5,r5
	xor	r6,r6
	add	r5,r4
MUL_REP:add	r6,r3
	dec	r5
	cmp	r5,0
	bne	MUL_REP

	pop	r5
	ret
START:
	add	r3,8	
	add	r4,4
	call	MUL
	END

;sfarsit