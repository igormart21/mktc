# 🚀 Guia de Deploy - AgroMarketplace

## Atualizações Implementadas

### ✅ Carrossel de Imagens
- **5 imagens** rotacionando automaticamente
- **Background da seção Hero** com efeito glassmorphism
- **Fundo cinza claro** para melhor contraste
- **Texto legível** com gradiente verde preservado
- **Design responsivo** para mobile

## 📋 Passos para Deploy

### 1. Acessar o Servidor
```bash
ssh root@agromaisdigital.com.br
```

### 2. Navegar para o Projeto
```bash
cd /opt/agromais
```

### 3. Executar Deploy
```bash
# Opção 1: Usar o script atualizado
./update.sh

# Opção 2: Executar comandos manualmente
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py collectstatic --noinput --clear
python manage.py migrate
supervisorctl restart agromais:*
systemctl restart nginx
```

### 4. Verificar Status
```bash
# Verificar serviços
supervisorctl status agromais:*
systemctl status nginx

# Testar site
curl -I https://agromaisdigital.com.br
```

## 🔍 Verificações Pós-Deploy

### ✅ Funcionalidades a Verificar:
1. **Carrossel funcionando** na página inicial
2. **Imagens carregando** corretamente
3. **Texto legível** sobre o fundo cinza
4. **Responsividade** em dispositivos móveis
5. **Performance** do site

### 🌐 URLs de Teste:
- **Página Inicial**: https://agromaisdigital.com.br
- **Carrossel**: Verificar se as 5 imagens aparecem
- **Mobile**: Testar em dispositivos móveis

## 📁 Arquivos Modificados
- `templates/core/home.html` - Template com carrossel
- `static/img/JPG/carrossel1.jpg` até `carrossel5.jpg` - Imagens do carrossel

## 🛠️ Troubleshooting

### Se o carrossel não aparecer:
```bash
# Verificar arquivos estáticos
python manage.py collectstatic --noinput

# Verificar logs
tail -f /var/log/supervisor/agromais-stdout.log
```

### Se as imagens não carregarem:
```bash
# Verificar permissões
chmod 644 static/img/JPG/carrossel*.jpg

# Verificar se os arquivos existem
ls -la static/img/JPG/
```

## 📞 Suporte
Em caso de problemas, verificar:
1. Logs do supervisor
2. Logs do nginx
3. Status dos serviços
4. Permissões dos arquivos

---
**Deploy realizado com sucesso! 🎉** 