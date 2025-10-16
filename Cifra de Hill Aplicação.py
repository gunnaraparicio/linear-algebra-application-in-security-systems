class BancoDadosHill:
    def __init__(self):
        # Matriz chave para a cifra de Hill
        self.chave = [[5, 4], [21, 25]]
        # Calcular a inversa modular da matriz chave
        self.chave_inversa = self.inversa_modular(self.chave, 26)

        # Dicionário principal: {usuario: {senha: {}, dados: {servico: senha}}}
        self.banco_dados = {}

    def determinante_matriz(self, matriz):
        """Calcula o determinante de uma matriz 2x2"""
        return matriz[0][0] * matriz[1][1] - matriz[0][1] * matriz[1][0]

    def inversa_modular(self, matriz, modulo):
        """Calcula a inversa modular da matriz 2x2"""
        det = self.determinante_matriz(matriz) % modulo

        # Encontrar inverso multiplicativo do determinante
        inverso_det = None
        for i in range(modulo):
            if (det * i) % modulo == 1:
                inverso_det = i
                break

        if inverso_det is None:
            raise ValueError("Matriz não é invertível módulo 26")

        # Matriz adjunta
        adjunta = [
            [matriz[1][1], -matriz[0][1]],
            [-matriz[1][0], matriz[0][0]]
        ]

        # Inversa modular = (inverso_det * adjunta) mod modulo
        inversa = [
            [(inverso_det * adjunta[0][0]) % modulo, (inverso_det * adjunta[0][1]) % modulo],
            [(inverso_det * adjunta[1][0]) % modulo, (inverso_det * adjunta[1][1]) % modulo]
        ]

        return inversa

    def multiplicar_matriz_vetor(self, matriz, vetor):
        """Multiplica matriz 2x2 por vetor 2x1"""
        resultado = [
            (matriz[0][0] * vetor[0] + matriz[0][1] * vetor[1]) % 26,
            (matriz[1][0] * vetor[0] + matriz[1][1] * vetor[1]) % 26
        ]
        return resultado

    def texto_para_numero(self, texto):
        """Converte texto para números (A=0, B=1, ..., Z=25)"""
        numeros = []
        for char in texto:
            if char.isalpha():
                numeros.append(ord(char.upper()) - ord('A'))
        return numeros

    def numero_para_texto(self, numeros):
        """Converte números de volta para texto"""
        texto = ''
        for num in numeros:
            texto += chr(num + ord('A'))
        return texto

    def preparar_texto(self, texto):
        """Prepara o texto para criptografia, garantindo comprimento par"""
        texto = texto.upper().replace(' ', '')
        # Se comprimento for ímpar, adiciona 'X'
        if len(texto) % 2 != 0:
            texto += 'X'
        return texto

    def criptografar(self, texto):
        """Criptografa texto usando a cifra de Hill"""
        texto = self.preparar_texto(texto)
        numeros = self.texto_para_numero(texto)
        resultado = []

        for i in range(0, len(numeros), 2):
            bloco = [numeros[i], numeros[i + 1]]
            cifrado = self.multiplicar_matriz_vetor(self.chave, bloco)
            resultado.extend(cifrado)

        return self.numero_para_texto(resultado)

    def descriptografar(self, texto_cifrado):
        """Descriptografa texto usando a cifra de Hill"""
        numeros = self.texto_para_numero(texto_cifrado)
        resultado = []

        for i in range(0, len(numeros), 2):
            bloco = [numeros[i], numeros[i + 1]]
            decifrado = self.multiplicar_matriz_vetor(self.chave_inversa, bloco)
            resultado.extend(decifrado)

        texto_decifrado = self.numero_para_texto(resultado)
        # Remove 'X' adicionado durante a preparação (se houver)
        return texto_decifrado.rstrip('X')

    def criar_usuario(self, usuario, senha):
        """Cria novo usuário no sistema"""
        if usuario in self.banco_dados:
            print("✗ Usuário já existe!")
            return False

        if not senha.isalpha():
            print("✗ Erro: A senha deve conter apenas letras!")
            return False

        # Criptografa a senha do usuário
        senha_criptografada = self.criptografar(senha)

        # Cria estrutura do usuário
        self.banco_dados[usuario] = {
            'senha': senha_criptografada,
            'servicos': {}  # {servico: senha_criptografada}
        }

        print(f"✓ Usuário '{usuario}' criado com sucesso!")
        return True

    def fazer_login(self, usuario, senha):
        """Faz login no sistema"""
        if usuario not in self.banco_dados:
            print("✗ Usuário não encontrado!")
            return False

        if not senha.isalpha():
            print("✗ Erro: A senha deve conter apenas letras!")
            return False

        senha_criptografada = self.banco_dados[usuario]['senha']
        senha_descriptografada = self.descriptografar(senha_criptografada)

        if senha.upper() == senha_descriptografada:
            print("✓ Login realizado com sucesso!")
            return True
        else:
            print("✗ Senha incorreta!")
            return False

    def cadastrar_senha_servico(self, usuario, servico, senha_servico):
        """Cadastra senha para um serviço"""
        if not senha_servico.isalpha():
            print("✗ Erro: A senha deve conter apenas letras!")
            return False

        # Criptografa a senha do serviço
        senha_criptografada = self.criptografar(senha_servico)
        self.banco_dados[usuario]['servicos'][servico] = senha_criptografada

        print(f"✓ Senha para '{servico}' cadastrada com sucesso!")
        print(f"Senha criptografada: {senha_criptografada}")
        return True

    def mostrar_servicos(self, usuario):
        """Mostra todos os serviços e senhas do usuário"""
        servicos = self.banco_dados[usuario]['servicos']

        if not servicos:
            print("Nenhum serviço cadastrado.")
            return

        print(f"\n--- Serviços de {usuario} ---")
        for i, (servico, senha_cripto) in enumerate(servicos.items(), 1):
            senha_normal = self.descriptografar(senha_cripto)
            print(f"{i}. Serviço: {servico}")
            print(f"   Senha normal: {senha_normal}")
            print(f"   Senha criptografada: {senha_cripto}")
            print("-" * 40)

        return servicos

    def editar_senha_servico(self, usuario, servicos):
        """Permite editar a senha de um serviço"""
        try:
            numero = int(input("Digite o número do serviço que deseja editar: ")) - 1
            lista_servicos = list(servicos.keys())

            if 0 <= numero < len(lista_servicos):
                servico = lista_servicos[numero]
                nova_senha = input(f"Digite a nova senha para {servico} (apenas letras): ").strip()

                if not nova_senha.isalpha():
                    print("✗ Erro: A senha deve conter apenas letras!")
                    return

                if self.cadastrar_senha_servico(usuario, servico, nova_senha):
                    print("✓ Senha atualizada com sucesso!")
            else:
                print("✗ Número inválido!")
        except ValueError:
            print("✗ Digite um número válido!")


def menu_principal():
    """Menu principal do sistema"""
    banco = BancoDadosHill()

    while True:
        print("\n" + "=" * 50)
        print("        Gerenciador de Senhas com Cifra de Hill")
        print("=" * 50)
        print("1. Criar usuário")
        print("2. Fazer login")
        print("3. Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '1':
            print("\n--- Criar Novo Usuário ---")
            usuario = input("Digite o nome de usuário: ").strip()
            senha = input("Digite a senha (apenas letras): ").strip()

            if usuario and senha:
                banco.criar_usuario(usuario, senha)
            else:
                print("✗ Usuário e senha não podem estar vazios!")

        elif opcao == '2':
            print("\n--- Fazer Login ---")
            usuario = input("Digite o nome de usuário: ").strip()
            senha = input("Digite a senha: ").strip()

            if usuario and senha:
                if banco.fazer_login(usuario, senha):
                    menu_usuario(banco, usuario)
            else:
                print("✗ Usuário e senha não podem estar vazios!")

        elif opcao == '3':
            print("Saindo do sistema... Até logo!")
            break

        else:
            print("✗ Opção inválida! Digite 1, 2 ou 3.")


def menu_usuario(banco, usuario):
    """Menu após o login do usuário"""
    while True:
        print("\n" + "=" * 50)
        print(f"        Bem-vindo, {usuario}!")
        print("=" * 50)
        print("1. Cadastrar nova senha de serviço")
        print("2. Acessar senhas salvas")
        print("3. Sair (logout)")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == '1':
            print("\n--- Cadastrar Nova Senha ---")
            servico = input("Digite o nome do serviço (ex: Facebook, Gmail): ").strip()
            senha_servico = input("Digite a senha (apenas letras): ").strip()

            if servico and senha_servico:
                banco.cadastrar_senha_servico(usuario, servico, senha_servico)
            else:
                print("✗ Serviço e senha não podem estar vazios!")

        elif opcao == '2':
            print("\n--- Acessar Senhas Salvas ---")
            servicos = banco.mostrar_servicos(usuario)

            if servicos:
                while True:
                    print("\nOpções:")
                    print("1. Editar uma senha")
                    print("2. Voltar ao menu anterior")

                    sub_opcao = input("Escolha uma opção: ").strip()

                    if sub_opcao == '1':
                        banco.editar_senha_servico(usuario, servicos)
                    elif sub_opcao == '2':
                        break
                    else:
                        print("✗ Opção inválida!")

        elif opcao == '3':
            print("Saindo da conta...")
            break

        else:
            print("✗ Opção inválida! Digite 1, 2 ou 3.")


if __name__ == "__main__":
    # Teste rápido da cifra
    print("=== SISTEMA DE GERENCIAMENTO DE SENHAS ===")
    print("Cifra de Hill ativa com matriz: [[5, 4], [21, 25]]")

    # Iniciar o sistema
    menu_principal()