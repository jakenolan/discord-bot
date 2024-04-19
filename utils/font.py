from re import findall, sub


# Init reference dict
ref = {}
ref['lowercase'] = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
ref['uppercase'] = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
ref['numbers'] = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
ref['special'] = [' ', '.', '?', '!', '-', '/', '\\', '(', ')', '@', ':', ';'] # Does not change for diff fonts


# Init monospace dict
monospace = {}
monospace['lowercase'] = ['𝚊', '𝚋', '𝚌', '𝚍', '𝚎', '𝚏', '𝚐', '𝚑', '𝚒', '𝚓', '𝚔', '𝚕', '𝚖', '𝚗', '𝚘', '𝚙', '𝚚', '𝚛', '𝚜', '𝚝', '𝚞', '𝚟', '𝚠', '𝚡', '𝚢', '𝚣']
monospace['uppercase'] = ['𝙰', '𝙱', '𝙲', '𝙳', '𝙴', '𝙵', '𝙶', '𝙷', '𝙸', '𝙹', '𝙺', '𝙻', '𝙼', '𝙽', '𝙾', '𝙿', '𝚀', '𝚁', '𝚂', '𝚃', '𝚄', '𝚅', '𝚆', '𝚇', '𝚈', '𝚉']
monospace['numbers'] = ['𝟶', '𝟷', '𝟸', '𝟹', '𝟺', '𝟻', '𝟼', '𝟽', '𝟾', '𝟿']
monospace['special'] = [' ', '.', '?', '!', '-', '/', '\\', '(', ')', '@', ':', ';'] # Same as ref


def convert_font(message):
    # Init variables
    mentions = []
    old = message
    new = ''

    # Catch any @s and replace with placeholder ⊶
    if '<@!' in old:
        old = old.replace('<@!', '<@')
        mentions = findall(r'<@.*?>', old)
        old = sub(r'<@.*?>', '⊶', old)

    # Parse message characters for converting to new font
    for c in old:
        # Set check to false for each character
        check = False
        # Find key and index of character and then convert
        for key in ref.keys():
            if c in ref[key]:
                index = ref[key].index(c)
                new += monospace[key][index]
                check = True
        # Final check to see if character was converted
        if check != True:
            new += c

    # Add all @s back into new
    if '⊶' in new:
        counter = 0
        for c in new:
            if c == '⊶':
                new = new.replace('⊶', mentions[counter], 1)
                counter += 1

    # Return converted message
    return new