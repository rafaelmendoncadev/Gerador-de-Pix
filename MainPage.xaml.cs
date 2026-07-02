using System.Globalization;
using Gerador_de_Pix.Models;
using Gerador_de_Pix.Services;
using QRCoder;

namespace Gerador_de_Pix;

public partial class MainPage : ContentPage
{
    /// <summary>Payload "copia e cola" gerado (mantido para cópia e envio).</summary>
    private string _copiaECola = string.Empty;

    /// <summary>Caminho absoluto do PNG do QR Code salvo no dispositivo.</summary>
    private string _caminhoQrCode = string.Empty;

    /// <summary>Último valor válido gerado (usado na mensagem do WhatsApp).</summary>
    private decimal _valorAtual;

    public MainPage()
    {
        InitializeComponent();
    }

    /// <summary>Gera o BR Code (copia e cola) e o QR Code a partir dos campos do formulário.</summary>
    private async void OnGerarClicked(object? sender, EventArgs e)
    {
        string nome = NomeEntry.Text?.Trim() ?? string.Empty;
        string whatsapp = WhatsAppEntry.Text?.Trim() ?? string.Empty;
        string descricao = DescricaoEntry.Text?.Trim() ?? string.Empty;
        string valorTexto = ValorEntry.Text?.Trim() ?? string.Empty;

        // --- Validações ---
        if (string.IsNullOrWhiteSpace(nome))
        {
            await DisplayAlertAsync("Atenção", "Informe o nome do cliente.", "OK");
            return;
        }
        if (string.IsNullOrWhiteSpace(whatsapp))
        {
            await DisplayAlertAsync("Atenção", "Informe o WhatsApp do cliente.", "OK");
            return;
        }

        // Tenta converter o valor digitado (aceita "10" ou "10,50").
        decimal? valor = null;
        if (!string.IsNullOrWhiteSpace(valorTexto))
        {
            valorTexto = valorTexto.Replace('.', ',');
            if (!decimal.TryParse(valorTexto, NumberStyles.Any, CultureInfo.GetCultureInfo("pt-BR"), out decimal v) || v <= 0)
            {
                await DisplayAlertAsync("Atenção", "Informe um valor válido maior que zero (ex.: 10,00).", "OK");
                return;
            }
            valor = v;
        }

        // --- Geração do payload BR Code ---
        _copiaECola = BrCodeService.Gerar(PixConfig.Nome, PixConfig.Chave, PixConfig.Cidade, valor);
        _valorAtual = valor ?? 0m;

        // --- Geração do QR Code (PNG) ---
        byte[] png = GerarQrCodePng(_copiaECola);
        _caminhoQrCode = await SalvarPngAsync(png);

        // Exibe a imagem
        QrCodeImage.Source = ImageSource.FromStream(() => new MemoryStream(png));

        // Exibe a chave copia e cola
        CopiaEColaLabel.Text = _copiaECola;

        // Mostra a área de resultado
        ResultadoBorder.IsVisible = true;

        await DisplayAlertAsync("Pronto!", "Pix gerado com sucesso.", "OK");
    }

    /// <summary>Copia a chave "copia e cola" para a área de transferência.</summary>
    private async void OnCopiarClicked(object? sender, EventArgs e)
    {
        await Clipboard.Default.SetTextAsync(_copiaECola);
        await DisplayAlertAsync("Copiado", "Chave copia e cola copiada para a área de transferência.", "OK");
    }

    /// <summary>Abre o WhatsApp com a mensagem de cobrança pré-preenchida.</summary>
    private async void OnEnviarWhatsClicked(object? sender, EventArgs e)
    {
        if (string.IsNullOrEmpty(_copiaECola))
        {
            await DisplayAlertAsync("Atenção", "Gere o Pix antes de enviar.", "OK");
            return;
        }
        await WhatsAppService.EnviarMensagemAsync(
            WhatsAppEntry.Text ?? string.Empty,
            NomeEntry.Text ?? string.Empty,
            DescricaoEntry.Text ?? string.Empty,
            _valorAtual,
            _copiaECola);
    }

    /// <summary>Compartilha a imagem do QR Code via sheet do sistema.</summary>
    private async void OnCompartilharQrClicked(object? sender, EventArgs e)
    {
        if (string.IsNullOrEmpty(_caminhoQrCode) || !File.Exists(_caminhoQrCode))
        {
            await DisplayAlertAsync("Atenção", "Gere o Pix antes de compartilhar.", "OK");
            return;
        }
        await WhatsAppService.CompartilharQrCodeAsync(_caminhoQrCode);
    }

    /// <summary>Gera o QR Code em bytes PNG a partir do payload.</summary>
    private static byte[] GerarQrCodePng(string payload)
    {
        using var gerador = new QRCodeGenerator();
        using var dados = gerador.CreateQrCode(payload, QRCodeGenerator.ECCLevel.M);
        using var png = new PngByteQRCode(dados);
        return png.GetGraphic(20);
    }

    /// <summary>Salva o PNG na pasta de dados do app e retorna o caminho absoluto.</summary>
    private static async Task<string> SalvarPngAsync(byte[] png)
    {
        string dir = FileSystem.AppDataDirectory;
        string caminho = Path.Combine(dir, $"qrcode_pix_{DateTime.Now:yyyyMMdd_HHmmss}.png");
        await File.WriteAllBytesAsync(caminho, png);
        return caminho;
    }
}
