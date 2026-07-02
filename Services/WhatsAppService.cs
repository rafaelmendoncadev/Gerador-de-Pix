using System.Globalization;
using System.Text;
using Gerador_de_Pix.Models;

namespace Gerador_de_Pix.Services;

/// <summary>
/// Monta a mensagem de cobrança e abre o WhatsApp.
/// </summary>
/// <remarks>
/// Observação importante: o link wa.me só permite pré-preencher TEXTO na conversa;
/// não é possível anexar uma imagem automaticamente. Por isso a imagem do QR Code
/// é compartilhada separadamente via <see cref="Share.Default"/>.
/// </remarks>
public static class WhatsAppService
{
    /// <summary>
    /// Constrói a mensagem de texto do Pix e abre o WhatsApp do destinatário.
    /// </summary>
    /// <param name="whatsapp">Número de WhatsApp do cliente (qualquer formato).</param>
    /// <param name="nomeCliente">Nome do cliente (para a saudação).</param>
    /// <param name="descricao">Descrição do produto/serviço (ex.: "Recarga New One").</param>
    /// <param name="valor">Valor da cobrança.</param>
    /// <param name="copiaECola">Chave "copia e cola" (payload BR Code).</param>
    public static async Task EnviarMensagemAsync(string whatsapp, string nomeCliente, string descricao, decimal valor, string copiaECola)
    {
        string numero = NormalizarNumero(whatsapp);
        string mensagem = MontarMensagem(nomeCliente, descricao, valor, copiaECola);
        string url = $"https://wa.me/{numero}?text={Uri.EscapeDataString(mensagem)}";
        await Launcher.OpenAsync(url);
    }

    /// <summary>
    /// Compartilha o arquivo de imagem do QR Code via sheet de compartilhamento do sistema
    /// (funciona no Windows e no Android).
    /// </summary>
    /// <param name="caminhoImagem">Caminho absoluto do arquivo PNG do QR Code.</param>
    public static async Task CompartilharQrCodeAsync(string caminhoImagem)
    {
        await Share.Default.RequestAsync(new ShareFileRequest
        {
            Title = "QR Code Pix",
            File = new ShareFile(caminhoImagem)
        });
    }

    /// <summary>
    /// Normaliza o número: mantém apenas dígitos e adiciona o DDI 55 (Brasil)
    /// caso ainda não esteja presente.
    /// </summary>
    private static string NormalizarNumero(string numero)
    {
        string digitos = new string(numero.Where(char.IsDigit).ToArray());

        // Já inclui DDI 55
        if (digitos.Length > 12 && digitos.StartsWith("55", StringComparison.Ordinal))
            return digitos;

        // Número brasileiro sem DDI -> adiciona 55
        if (digitos.Length >= 10 && digitos.Length <= 11)
            return "55" + digitos;

        return digitos;
    }

    /// <summary>
    /// Monta o corpo da mensagem enviada ao cliente.
    /// </summary>
    private static string MontarMensagem(string nomeCliente, string descricao, decimal valor, string copiaECola)
    {
        string primeiroNome = ObterPrimeiroNome(nomeCliente);
        string valorStr = valor.ToString("C", CultureInfo.GetCultureInfo("pt-BR"));

        var sb = new StringBuilder();
        sb.AppendLine($"Olá {primeiroNome}! 🙋");
        sb.AppendLine();
        sb.AppendLine("Seguem os dados para pagamento via Pix:");
        sb.AppendLine();
        sb.AppendLine($"📌 *Recebedor:* {PixConfig.Nome}");
        sb.AppendLine($"🆔 *Tipo:* {PixConfig.Tipo}");
        sb.AppendLine($"🔑 *Chave:* {PixConfig.Chave}");
        sb.AppendLine($"📍 *Cidade:* {PixConfig.Cidade}");
        if (!string.IsNullOrWhiteSpace(descricao))
            sb.AppendLine($"📝 *Descrição:* {descricao}");
        sb.AppendLine($"💰 *Valor:* {valorStr}");
        sb.AppendLine();
        sb.AppendLine("📲 *Chave Pix Copia e Cola:*");
        sb.AppendLine(copiaECola);
        sb.AppendLine();
        sb.AppendLine("ℹ️ Você pode pagar escaneando o QR Code (que enviarei a seguir) ou colando a chave acima no app do seu banco.");
        sb.AppendLine();
        sb.AppendLine("✅ Assim que efetuar o pagamento, por favor, me envie o *comprovante* para confirmação.");
        sb.AppendLine();
        sb.AppendLine("Obrigado! 🙏");
        return sb.ToString();
    }

    private static string ObterPrimeiroNome(string nomeCompleto)
    {
        if (string.IsNullOrWhiteSpace(nomeCompleto)) return string.Empty;
        return nomeCompleto.Trim().Split(' ', 2, StringSplitOptions.RemoveEmptyEntries)[0];
    }
}
