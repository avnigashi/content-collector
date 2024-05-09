import re

class FileMinifier:
    """Utility class to handle file content minification and long string removal."""
    @staticmethod
    def minify_content(file_content):
        """Minify content by removing comments and unnecessary whitespaces."""
        file_content = re.sub(r'//.*?$', '', file_content, flags=re.MULTILINE)  # Remove single-line comments
        file_content = re.sub(r'/\*.*?\*/', '', file_content, flags=re.DOTALL)  # Remove block comments
        file_content = re.sub(r'\s+', ' ', file_content).strip()  # Remove extra whitespace
        return file_content

    @staticmethod
    def remove_long_strings(file_content, max_length=100):
        """Remove or replace long strings in the file content."""
        def replace_long_strings(match):
            string = match.group(0)
            if len(string) > max_length:
                # Return an indicator like "<removed>" or truncate the string
                return '"<removed>"'  # You could also truncate the string here
            return string

        # This regex finds strings within double or single quotes
        file_content = re.sub(r'"[^"]*"|\'[^\']*\'', replace_long_strings, file_content)
        return file_content
