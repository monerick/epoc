import hmac
import hashlib
import base64
import json
from config import Config


class CaesarCipher:
    def __init__(self, shift=None):
        self.shift = shift if shift is not None else Config.CAESAR_SHIFT

    def _rotate_char(self, char, shift):
        if "A" <= char <= "Z":
            return chr((ord(char) - ord("A") + shift) % 26 + ord("A"))
        if "a" <= char <= "z":
            return chr((ord(char) - ord("a") + shift) % 26 + ord("a"))
        if "0" <= char <= "9":
            return chr((ord(char) - ord("0") + shift) % 10 + ord("0"))
        return char

    def encrypt(self, plaintext):
        if not isinstance(plaintext, str):
            plaintext = str(plaintext)
        return "".join(self._rotate_char(c, self.shift) for c in plaintext)

    def decrypt(self, ciphertext):
        if not isinstance(ciphertext, str):
            ciphertext = str(ciphertext)
        return "".join(self._rotate_char(c, -self.shift) for c in ciphertext)

    def encrypt_with_rotating_shift(self, plaintext, base_shift=None):
        if base_shift is None:
            base_shift = self.shift
        result = []
        for i, c in enumerate(plaintext):
            dynamic_shift = base_shift + (i % 5)
            result.append(self._rotate_char(c, dynamic_shift))
        return "".join(result)

    def decrypt_with_rotating_shift(self, ciphertext, base_shift=None):
        if base_shift is None:
            base_shift = self.shift
        result = []
        for i, c in enumerate(ciphertext):
            dynamic_shift = base_shift + (i % 5)
            result.append(self._rotate_char(c, -dynamic_shift))
        return "".join(result)


class SecurePayload:
    def __init__(self):
        self.cipher = CaesarCipher()
        self.secret = Config.SECRET_KEY.encode("utf-8")

    def _hmac_sign(self, data_str):
        return hmac.new(self.secret, data_str.encode("utf-8"), hashlib.sha256).hexdigest()

    def _hmac_verify(self, data_str, signature):
        expected = self._hmac_sign(data_str)
        return hmac.compare_digest(expected, signature)

    def encode(self, data):
        if isinstance(data, (dict, list)):
            data = json.dumps(data, separators=(",", ":"))
        caesar_layer = self.cipher.encrypt_with_rotating_shift(data)
        signature = self._hmac_sign(caesar_layer)
        encoded = base64.urlsafe_b64encode(
            json.dumps({"d": caesar_layer, "s": signature}).encode("utf-8")
        ).decode("utf-8")
        return encoded

    def decode(self, encoded_str):
        try:
            decoded = base64.urlsafe_b64decode(encoded_str.encode("utf-8")).decode("utf-8")
            payload = json.loads(decoded)
            caesar_layer = payload["d"]
            signature = payload["s"]
            if not self._hmac_verify(caesar_layer, signature):
                raise ValueError("Firma HMAC invalida: integridad comprometida")
            plain = self.cipher.decrypt_with_rotating_shift(caesar_layer)
            try:
                return json.loads(plain)
            except (json.JSONDecodeError, TypeError):
                return plain
        except (ValueError, KeyError, json.JSONDecodeError, Exception) as e:
            raise ValueError(f"Error de descifrado: {e}")
