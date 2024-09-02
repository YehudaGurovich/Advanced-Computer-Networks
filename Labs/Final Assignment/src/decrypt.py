import re
from base64 import b64decode


def decrypt_column_cipher(key: str, encrypted_message: str) -> str:
    """
    Decrypt a message that was encrypted using the columnar cipher.
    """
    # Calculate the number of rows
    key_length = len(key)
    message_length = len(encrypted_message)
    num_rows = (message_length + key_length - 1) // key_length

    # Create sorted column indices (same as in encryption)
    column_indices = sorted(range(key_length), key=lambda k: key[k])

    # Create empty matrix
    matrix = [[''] * key_length for _ in range(num_rows)]

    # Fill the matrix column by column
    char_index = 0
    for col in column_indices:
        for row in range(num_rows):
            matrix[row][col] = encrypted_message[char_index]
            char_index += 1

    # Read the matrix row by row
    decrypted_message = ''.join(''.join(row) for row in matrix)

    # Remove padding
    return decrypted_message.rstrip('*').replace('*', ' ')


def reorganize_packets(packets: str, split_length: int) -> str:
    """
    Reorganize the packets to extract the hidden message. Make sure packets is formatted correctly.
    """
    packets = packets.split('.')
    # Extract the packets that contain "ctf"
    packets = [re.sub(r'(ctf\d{2}).*', r'\1', packet)
               for packet in packets if 'ctf' in packet]
    # Obtain the last split_length characters of each packet
    packets = [packet[-split_length:] for packet in packets]
    # Sort the packets by the integer value of the last two characters
    packets = sorted(packets, key=lambda packet: int(packet[-2:]))
    hidden_message = ''.join(packet[:-5] for packet in packets)
    return b64decode(hidden_message).decode().rstrip('\x00')


if __name__ == "__main__":
    key = "RAVEN"
    packets = ".3...'........E..1....@.~....YE..\"F.$N....ZSpvaVUqa2QqbWlpctf04.$.bb...?..'..E..1....@........H...<....BNd1uNyTFdrYgFfWnkftc076...<.}.Lq.G..E..1....@..+...K..W.t{.Z..#AR2z38SVE6kPKU9wyftc02'.Ln>.!.i.....E..1....@.d......I..\"-....3.soTvvW8RV92EBBhnftc01e!....0.......E..1....@.'..:	. ...5.`.....5jOSkx4QSRSBIcGnftc03..s*ch.|.....E..1....@.7..59V....^.a....aGdlb2QqKiptbm9jctf00T.*....5p.jI..E..1....@.-.....?.Q.. ....t.eWF0cyEqKmcqeWF2ctf07....y......m..E..1....@.a...Q..+TW......V4HXHksPxSg8ICG3rgftc01.|....m.Q.....E..1....@...m......./(#...h.Y2llZWZ3c2lsKi5Sctf08.PZ...X9\\.....E..1....@........{$....3...czn6TLUWws8jN0PMYftc10e..@.G..m.....E..1....@.....m/..\\...\".....f4gxuvxLRsmBhGaZftc01$..W.&o.X.\"...E..1....@.tbo..D.6.C.M....y.aEghAAAAAAAAAAAActf11...2!...!.....E..1....@.7@t......C'......@uNp0TDoYt2wixqNKftc07..w..n...Z_...E..1....@.Z.....Dg...j.r..p.YW9zdWV0Zll1byp0ctf09.Q..\"....{.	..E..1....@.R............#..z.UK6zhnHRSFoIMKCiftc11..1>...W......E..1....@..l....\\.f!c.....BvxUzCab4owumdtH3Tftc015...;.v$..sd..E..1....@..:x:.. r> ........cnV0Km8uZG8uZm1nctf05;K..5...F~.Y..E..1....@.....oR!.ib...E..\\.hq8IzmSQd3RUcI2sftc00.w&..ui.7.....E..1....@...[m..............7A3Jin1xzw5Wrpj2ftc01..Ea.P........E..1....@.2.....W.<Nb.....!Q7MkAWEA0uvLSjDMUftc10..w. ...8.....E..1....@.`{..........Kr....W7BBGSXDp7mlXmtEftc09.F....g.P{jG..E..1....@.U......)...'*.....ZWdpb25zKmloKm5sctf01....z.G .d.d..E..1....@.'Z..>.xn.}d.TO....4yuiUd8RVvFl6R4Dftc00j6(...........E..1....@.....-.\".....}.....d3RmdXJoL2xhb2Qqctf03'S%b.NO9..-...E..1....@....d.3..........l.y8RDHUAg6bNdYfhxftc08T8l.%.L.......E..1....@.;d.3.*.W...Y....a.KippaGFmc1IqVCpuctf06:.?..a.r.)....E..1....@.G..L.>qaVBP..@....aHVjbWFzdG5vYmQqctf10. .xs.....N...E..1....@..#......\\7...z....dCpZbm9zKipoYW9zctf02.A....ov......E..1....@...\".#r...Co.....K+LTtlKBoNRy8in1Maftc11"
    encrypted_message = reorganize_packets(packets, 21)
    message = decrypt_column_cipher(key, encrypted_message)
    print(f"Decrypted message: {message}")
