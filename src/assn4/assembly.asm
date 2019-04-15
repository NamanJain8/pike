global main 
section .data
    print_int db "%i ", 0x00
    print_line db "", 0x0a, 0x00
section .text
main:
    push ebp
    mov ebp, esp
    sub esp, 0
    mov edi, 1
    mov [ebp-8], edi
    mov edi, [ebp-8]
    mov esi, [ebp-4]
    add edi, esi
    mov [ebp-12], edi
    mov edi, [ebp-12]
    mov [ebp+0], edi
    mov esp, ebp
    pop ebp
    mov eax, 1
    mov ebx, 0
    int 0x80
    
