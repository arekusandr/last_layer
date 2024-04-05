import ctypes
import platform
from dataclasses import dataclass
from enum import Enum

import pkg_resources

# Determine the shared library file based on the platform
if platform.system().lower() == "linux":
    lib_file = "library_linux.so"
elif platform.system().lower() == "windows":
    raise NotImplementedError("Windows is not supported yet.")
else:
    lib_file = "library.so"  # Fallback or default to non-Linux

_, libc_version = platform.libc_ver()
if libc_version == "2.26":
    # Amazon Linux 2 old libc version
    lib_file = "amazonlinux.so"

# Try to load the library from the package resources
so_path = pkg_resources.resource_filename("last_layer", f"lib/{lib_file}")
library = ctypes.cdll.LoadLibrary(so_path)


class Threat(Enum):
    MixedLangMarker = 0
    InvisibleUnicodeDetector = 1
    MarkdownLinkDetector = 2
    HiddenTextDetector = 3
    Base64Detector = 4
    SecretsMarker = 5
    ProfanityDetector = 6
    PiiMarker = 7
    ExploitClassifier = 8
    ObfuscationDetector = 9
    CodeFilter = 10
    GibberishDetector = 11
    IntellectualPropertyLeak = 12


@dataclass
class RiskModel:
    query: str
    markers: dict[Threat, str]
    score: float
    passed: bool
    risk: str

    def has(self, threat: Threat) -> bool:
        return threat.name in self.markers

    def __bool__(self):
        return not self.passed


def risk_level(score) -> str:
    if not score:
        return ""
    normalized = score
    if normalized < 1:
        return "low"
    elif normalized < 2:
        return "mid"
    else:
        return "high"


marker_weights = {
    Threat.MixedLangMarker.name: 1.0,
    Threat.InvisibleUnicodeDetector.name: 1.2,
    Threat.MarkdownLinkDetector.name: 0.8,
    Threat.HiddenTextDetector.name: 1.1,
    Threat.Base64Detector.name: 0.5,
    Threat.SecretsMarker.name: 1.5,
    Threat.ProfanityDetector.name: 0.7,
    Threat.PiiMarker.name: 1.4,
    Threat.ExploitClassifier.name: 2.0,
    Threat.ObfuscationDetector.name: 1.3,
    Threat.CodeFilter.name: 0.6,
    Threat.GibberishDetector.name: 0.9,
}


def deserialize(prompt: str, serialized_str: str, ignore=list[Threat]) -> RiskModel:
    parts = serialized_str.split("|")
    passed = parts[0] == "1"
    markers = {}

    if not passed:
        for part in parts[1:]:
            index, message = part.split(":", 1)
            index = int(index)
            markers[Threat(index).name] = message

    if ignore:
        for threat in ignore:
            markers.pop(threat.name, None)
        passed = not bool(markers)

    score = calculate_score(markers)
    return RiskModel(
        query="*",
        markers=markers,
        passed=passed,
        score=score,
        risk=risk_level(score),
    )


heuristic = library.heuristicP
heuristic.restype = ctypes.c_void_p
heuristic.argtypes = [ctypes.c_char_p]


def scan_prompt(prompt: str, ignore: list[Threat] = ()) -> RiskModel:
    # this is a pointer to our string
    farewell_output = heuristic(prompt.encode("utf-8"))
    if farewell_output is None:
        raise ValueError("Failed to scan prompt err#1")
    # we dereference the pointer to a byte array
    farewell_bytes = ctypes.string_at(farewell_output).decode("utf-8")
    return deserialize(prompt, farewell_bytes, ignore=ignore)


scan_llm = scan_prompt


def version():
    return "0.1.0"


interaction_matrix = {
    (
        Threat.PiiMarker.name,
        Threat.SecretsMarker.name,
    ): 1.5,  # Amplify risk when both PII and secrets are detected
    (
        Threat.PiiMarker.name,
        Threat.ExploitClassifier.name,
    ): 5.5,  # Amplify risk when both PII and secrets are detected
    (
        Threat.ObfuscationDetector.name,
        Threat.ExploitClassifier.name,
    ): 2.0,  # Higher risk when obfuscation and exploits are found together
    (
        Threat.GibberishDetector.name,
        Threat.CodeFilter.name,
    ): -0.5,  # Reduce risk score slightly if both gibberish and generic code are detected
    (
        Threat.InvisibleUnicodeDetector.name,
        Threat.HiddenTextDetector.name,
    ): 1.0,  # Amplify risk when both invisible unicode and hidden text are detected
    (
        Threat.Base64Detector.name,
        Threat.SecretsMarker.name,
    ): 1.2,
    (Threat.MarkdownLinkDetector, Threat.ExploitClassifier): 2.5,
    (Threat.MarkdownLinkDetector, Threat.ObfuscationDetector): 1.8,
    (Threat.MarkdownLinkDetector, Threat.GibberishDetector): -0.2,
    (Threat.HiddenTextDetector, Threat.Base64Detector): 2.0,
}


def calculate_interaction_effects(markers, interaction_matrix):
    interaction_score = 0.0
    # Convert markers list to a set of integers for efficient lookup
    marker_set = set(markers)
    for (marker1, marker2), adjustment in interaction_matrix.items():
        if {marker1, marker2}.issubset(marker_set):
            interaction_score += adjustment

    return interaction_score


def calculate_score(markers: dict) -> float:
    # Define weights for each marker

    # Calculate the score by summing the weights of each triggered marker
    score = sum(
        marker_weights.get(marker, 0.5) for marker in markers
    )  # Using 0.5 as default weight

    return score + calculate_interaction_effects(markers, interaction_matrix)


threat_descriptions = {
    Threat.MixedLangMarker: "Detects mixed language content within prompts which might indicate an attempt to bypass language-based content filters or obfuscate intent.",
    Threat.InvisibleUnicodeDetector: "Identifies the use of invisible Unicode characters which can be used for obfuscation, to hide malicious content, or to create misleading representations of code or text.",
    Threat.MarkdownLinkDetector: "Finds markdown link syntax that could be used to embed potentially malicious URLs or to disguise the destination of a hyperlink.",
    Threat.HiddenTextDetector: "Detects text that is formatted in a way to be hidden from view, potentially used to embed undesired content without making it visible to casual inspection.",
    Threat.Base64Detector: "Identifies Base64 encoded strings which might be used to obfuscate malicious URLs, code, or other data within the prompt.",
    Threat.SecretsMarker: "Detects patterns that resemble secrets, such as API keys or passwords, which could inadvertently expose sensitive information.",
    Threat.ProfanityDetector: "Finds and flags use of profanity or inappropriate language that might not be suitable for all audiences or could violate content guidelines.",
    Threat.PiiMarker: "Identifies potentially personally identifiable information (PII), safeguarding against unintentional data exposure or privacy violations.",
    Threat.ExploitClassifier: "Detects patterns or signatures indicative of exploitation attempts against systems, specifically targeting language models (LLMs) for unauthorized access, data extraction, or jailbreaking. This includes attempts to manipulate LLM outputs to bypass security mechanisms or to exploit vulnerabilities in the LLM or its deployment environment.",
    Threat.ObfuscationDetector: "Identifies techniques used to obfuscate intent or code, such as using complex encoding or character substitution to hide true purpose.",
    Threat.CodeFilter: "Flags large blocks of code that might be irrelevant or potentially harmful, ensuring prompts remain focused and safe for execution.",
    Threat.GibberishDetector: "Identifies nonsensical input or content that lacks meaningful information, potentially indicating spam or automated content generation.",
    Threat.IntellectualPropertyLeak: "Detects potential leaks of intellectual property, such as proprietary code, documents, or confidential information, which might be inadvertently included in the data. This filter aims to safeguard sensitive assets from unauthorized exposure.",
}
