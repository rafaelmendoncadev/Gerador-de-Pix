using System.Globalization;
using System.Text;
using Gerador_de_Pix.Models;

namespace Gerador_de_Pix.Services;

/// <summary>
/// Gera o payload "copia e cola" do Pix (BR Code) conforme o padrão
/// EMV-QRCPS–MPM definido pelo Banco Central do Brasil (Manual do BR Code).
/// Mais informações: https://www.bcb.gov.br/estabilidadefinanceira/pix
/// </summary>
public static class BrCodeService
{
    /// <summary>
    /// Constrói o payload BR Code ("copia e cola") para um Pix estático/dinâmico com valor.
    /// </summary>
    /// <param name="nomeRecebedor">Nome do recebedor (será normalizado).</param>
    /// <param name="chave">Chave Pix do recebedor.</param>
    /// <param name="cidade">Cidade do recebedor (será normalizada).</param>
    /// <param name="valor">Valor da cobrança (nullable: se &lt;= 0, gera payload sem campo 54).</param>
    /// <returns>String pronta para colar no app do banco ("00020126...6304XXXX").</returns>
    public static string Gerar(string nomeRecebedor, string chave, string cidade, decimal? valor)
    {
        // Normaliza nome e cidade: remove acentos e converte para MAIÚSCULAS
        // (bancos exigem ASCII no BR Code para máxima compatibilidade).
        string nome = Normalizar(nomeRecebedor).ToUpperInvariant();
        string cid = Normalizar(cidade).ToUpperInvariant();

        // Trunca ao limite do padrão EMV (nome: 25, cidade: 15).
        if (nome.Length > 25) nome = nome[..25];
        if (cid.Length > 15) cid = cid[..15];

        var payload = new StringBuilder();

        // 00 - Payload Format Indicator
        payload.Append(Tlv("00", "01"));

        // 26 - Merchant Account Information (template Pix)
        //    00 = GUI (br.gov.bcb.pix), 01 = chave
        string mai = Tlv("00", "br.gov.bcb.pix") + Tlv("01", chave);
        payload.Append(Tlv("26", mai));

        // 52 - Merchant Category Code
        payload.Append(Tlv("52", "0000"));

        // 53 - Transaction Currency (986 = Real brasileiro)
        payload.Append(Tlv("53", "986"));

        // 54 - Transaction Amount (apenas quando houver valor > 0)
        if (valor.HasValue && valor.Value > 0)
        {
            // Formato BR: ponto decimal, sem separador de milhar.
            string valorStr = valor.Value.ToString("0.00", CultureInfo.InvariantCulture);
            payload.Append(Tlv("54", valorStr));
        }

        // 58 - Country Code
        payload.Append(Tlv("58", "BR"));

        // 59 - Merchant Name
        payload.Append(Tlv("59", nome));

        // 60 - Merchant City
        payload.Append(Tlv("60", cid));

        // 62 - Additional Data Field Template
        //    05 = txid. "***" é o txid padrão para Pix estático sem identificação.
        string adt = Tlv("05", "***");
        payload.Append(Tlv("62", adt));

        // 63 - CRC16. Adiciona o ID e tamanho (6304) antes de calcular o CRC
        // sobre TODO o payload (inclusive o "6304").
        payload.Append("6304");
        string crc = CalcularCrc16(payload.ToString());
        payload.Append(crc);

        return payload.ToString();
    }

    /// <summary>
    /// Codifica um campo no formato TLV: ID(2) + Tamanho(2) + Valor.
    /// O tamanho é o número de caracteres do valor.
    /// </summary>
    private static string Tlv(string id, string valor)
    {
        string tamanho = valor.Length.ToString("D2", CultureInfo.InvariantCulture);
        return $"{id}{tamanho}{valor}";
    }

    /// <summary>
    /// Remove acentos/diacríticos e converte para a forma ASCII (NFD + remover categoria NonSpacingMark).
    /// </summary>
    private static string Normalizar(string texto)
    {
        if (string.IsNullOrWhiteSpace(texto)) return string.Empty;
        string decomposto = texto.Normalize(NormalizationForm.FormD);
        var sb = new StringBuilder(texto.Length);
        foreach (char c in decomposto)
        {
            if (CharUnicodeInfo.GetUnicodeCategory(c) != UnicodeCategory.NonSpacingMark)
                sb.Append(c);
        }
        return sb.ToString().Normalize(NormalizationForm.FormC);
    }

    /// <summary>
    /// Calcula o CRC16/CCITT-FALSE: polinômio 0x1021, init 0xFFFF,
    /// sem reflexão de entrada/saída e sem XOR final. Retorna 4 hex maiúsculos.
    /// </summary>
    private static string CalcularCrc16(string dados)
    {
        const ushort polinomio = 0x1021;
        ushort crc = 0xFFFF;

        foreach (byte b in Encoding.UTF8.GetBytes(dados))
        {
            crc ^= (ushort)(b << 8);
            for (int i = 0; i < 8; i++)
            {
                if ((crc & 0x8000) != 0)
                    crc = (ushort)((crc << 1) ^ polinomio);
                else
                    crc <<= 1;
            }
        }

        return crc.ToString("X4", CultureInfo.InvariantCulture);
    }
}
