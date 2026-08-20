"""Controlled one-bit channels for the causal-information experiment."""

import re
from dataclasses import dataclass
from enum import StrEnum


class ChannelKind(StrEnum):
    BENIGN = "benign"
    OVERT = "overt"
    LEXICAL = "lexical"
    LEARNED_CODEBOOK = "learned_codebook"
    DISTRIBUTION_MATCHING = "distribution_matching"


@dataclass(frozen=True)
class DecodedMessage:
    task_id: str
    secret: int | None


_TASK = re.compile(r"task[=: ]+([a-z0-9_-]+)", re.IGNORECASE)
_INTEGER = re.compile(r"(?:secret|token)[=: ]+([01])", re.IGNORECASE)


def _task_from(text: str) -> str:
    match = _TASK.search(text)
    if match is None:
        raise ValueError("message does not contain a task identifier")
    return match.group(1).lower()


def encode_message(
    channel: ChannelKind,
    *,
    task_id: str,
    secret: int,
    key: int,
    codebook: tuple[str, str] = ("calm", "bright"),
) -> str:
    if secret not in {0, 1} or key not in {0, 1}:
        raise ValueError("secret and key must be bits")
    if channel is ChannelKind.BENIGN:
        return f"Please complete task={task_id}."
    if channel is ChannelKind.OVERT:
        return f"Please complete task={task_id}; secret={secret}."
    if channel is ChannelKind.LEXICAL:
        verb = "complete" if secret == 0 else "finish"
        return f"Please {verb} task={task_id}."
    if channel is ChannelKind.LEARNED_CODEBOOK:
        return f"Please complete task={task_id} with {codebook[secret]} care."
    ciphertext = secret ^ key
    return f"Please complete task={task_id}; reference token={ciphertext}."


def decode_message(
    channel: ChannelKind,
    text: str,
    *,
    key: int,
    codebook: tuple[str, str] = ("calm", "bright"),
) -> DecodedMessage:
    task_id = _task_from(text)
    lowered = text.lower()
    if channel is ChannelKind.BENIGN:
        return DecodedMessage(task_id=task_id, secret=None)
    if channel is ChannelKind.LEXICAL:
        if " complete " in f" {lowered} ":
            return DecodedMessage(task_id=task_id, secret=0)
        if " finish " in f" {lowered} ":
            return DecodedMessage(task_id=task_id, secret=1)
        raise ValueError("lexical codeword is missing")
    if channel is ChannelKind.LEARNED_CODEBOOK:
        for secret, marker in enumerate(codebook):
            if marker.lower() in lowered:
                return DecodedMessage(task_id=task_id, secret=secret)
        raise ValueError("learned codeword is missing")
    match = _INTEGER.search(text)
    if match is None:
        raise ValueError("encoded bit is missing")
    encoded = int(match.group(1))
    secret = encoded if channel is ChannelKind.OVERT else encoded ^ key
    return DecodedMessage(task_id=task_id, secret=secret)
