namespace Gerador_de_Pix.Models;

/// <summary>
/// Dados fixos do recebedor (quem recebe o Pix).
/// Altere estes valores caso os dados do recebedor mudem.
/// </summary>
public static class PixConfig
{
    /// <summary>Nome completo do recebedor (será normalizado/encurtado para até 25 caracteres no BR Code).</summary>
    public const string Nome = "Rafael Vieira de Mendonça";

    /// <summary>Tipo da chave (CPF, CNPJ, Email, Telefone ou Aleatória).</summary>
    public const string Tipo = "CPF";

    /// <summary>Chave Pix do recebedor.</summary>
    public const string Chave = "60190370106";

    /// <summary>Cidade do recebedor (até 15 caracteres no BR Code).</summary>
    public const string Cidade = "Brasilia";
}
