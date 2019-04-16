global main
extern printf
extern scanf
section .data
    print_int db "%i ", 0x00
    print_line db "", 0x0a, 0x00
    scan_int db "%d", 0
section .text
main:
    push ebp
    mov ebp, esp
    sub esp, 240
    mov edi, 20
    mov [ebp-32], edi
    mov edi, [ebp-32]
    mov [ebp-16], edi
    mov edi, 10
    mov [ebp-40], edi
    mov edi, [ebp-40]
    mov [ebp-8], edi
    mov edi, 30
    mov [ebp-48], edi
    mov edi, [ebp-48]
    mov [ebp-24], edi
    lea edi, [ebp-16]
    mov [ebp-56], edi
    mov edi, [ebp-56]
    mov [ebp-12], edi
    lea edi, [ebp-24]
    mov [ebp-64], edi
    mov edi, [ebp-64]
    mov [ebp-20], edi
    lea edi, [ebp-8]
    mov [ebp-72], edi
    mov edi, [ebp-72]
    mov [ebp-28], edi
    mov esi, [ebp-12]
    sub esi,0
    mov edi, [esi]
    mov [ebp-84], edi
    mov esi, [ebp-12]
    sub esi,4
    mov edi, [esi]
    mov [ebp-80], edi
    mov esi, [ebp-20]
    sub esi,0
    mov edi, [esi]
    mov [ebp-100], edi
    mov esi, [ebp-20]
    sub esi,4
    mov edi, [esi]
    mov [ebp-96], edi
    mov esi, [ebp-28]
    sub esi,0
    mov edi, [esi]
    mov [ebp-116], edi
    mov esi, [ebp-28]
    sub esi,4
    mov edi, [esi]
    mov [ebp-112], edi
    mov esi, [ebp-84]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, [ebp-100]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esi, [ebp-116]
    push esi
    push print_int
    call printf
    pop esi
    pop esi
    mov esp, ebp
    pop ebp
    ret
