#!/usr/bin/env python

# Copyright (c) 2009-2012, Mario Vilas
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Unofficial pastebin.com API for Python
by Mario Vilas (mvilas at gmail dot com)

Unlike the official API, this one doesn't require an API key.

U{http://breakingcode.wordpress.com/2012/01/27/pasting-anonymously-to-pastebin-com/}

U{http://breakingcode.wordpress.com/2010/03/06/using-the-pastebin-api-with-python/}

Usage examples::
    >>> from pastebin import submit
    >>>
    >>> # Submit a simple text message.
    ... url = submit("This is a test message.")
    >>> print url
    http://pastebin.com/G4YWsB1a
    >>>
    >>> # Submit a simple "hello world" code in Python.
    ... # Paste expires in 10 minutes.
    ... url = submit("print \"Hello world!\"",
    ...               paste_format="python",
    ...               paste_expire_date="10M")
    >>> print url
    http://pastebin.com/rKEVDWHP
    >>>
    >>> # Submit Apache's logs as a private paste.
    ... # Give the paste a title.
    ... url = submit(open('/var/log/apache/access.log', 'r').read(),
    ...              paste_format="apache",
    ...              paste_private=True,
    ...              paste_name="My Apache access logs")
    >>> print url
    http://pastebin.com/kfepMRLh
    >>>
"""

__all__ = ['submit', 'Pastebin', 'PastebinError']

import urllib

class PastebinError(RuntimeError):
    """
    Pastebin API error.

    The error message returned by the web application is stored as the Python
    exception message.
    """

class Pastebin(object):
    """
    Unofficial python interface to the Pastebin legacy API.

    Unlike the official API, this one doesn't require an API key, so it's
    virtually anonymous.

    @warn: To be B{completely} anonymous you'll have to hide your IP address as
        well, either by using an HTTP proxy or the Tor network.

        To use an HTTP proxy, set the HTTP_PROXY environment variable as per
        the documentation of the Python standard C{urllib} module:
        U{http://docs.python.org/library/urllib.html}

        To go through the Tor network, consult the following Wiki document:
        U{https://trac.torproject.org/projects/tor/wiki/doc/TorifyHOWTO}

    @type paste_expire_date: tuple(str)
    @cvar paste_expire_date: Valid C{paste_expire_date} values, see L{submit}.

    @type paste_format: tuple(str)
    @cvar paste_format: Valid C{parse_format} values, see L{submit}.
    """

    # Base domain name
    _base_domain = 'pastebin.com'

    # Valid Pastebin URLs begin with this string
    _prefix_url = 'http://%s/' % _base_domain

    # Valid Pastebin URLs with a custom subdomain begin with this string
    _subdomain_url = 'http://%%s.%s/' % _base_domain

    # URL to the POST API
    _api_url = 'http://%s/api_public.php' % _base_domain

    # Valid paste_expire_date values
    paste_expire_date = ('N', '10M', '1H', '1D', '1M')

    # Valid parse_format values
    paste_format = (
        '4cs',              # 4CS
        '6502acme',         # 6502 ACME Cross Assembler
        '6502kickass',      # 6502 Kick Assembler
        '6502tasm',         # 6502 TASM/64TASS
        'abap',             # ABAP
        'actionscript',     # ActionScript
        'actionscript3',    # ActionScript 3
        'ada',              # Ada
        'algol68',          # ALGOL 68
        'apache',           # Apache Log
        'applescript',      # AppleScript
        'apt_sources',      # APT Sources
        'asm',              # ASM (NASM)
        'asp',              # ASP
        'autoconf',         # autoconf
        'autohotkey',       # Autohotkey
        'autoit',           # AutoIt
        'avisynth',         # Avisynth
        'awk',              # Awk
        'bascomavr',        # BASCOM AVR
        'bash',             # Bash
        'basic4gl',         # Basic4GL
        'bibtex',           # BibTeX
        'blitzbasic',       # Blitz Basic
        'bnf',              # BNF
        'boo',              # BOO
        'bf',               # BrainFuck
        'c',                # C
        'c_mac',            # C for Macs
        'cil',              # C Intermediate Language
        'csharp',           # C#
        'cpp',              # C++
        'cpp-qt',           # C++ (with QT extensions)
        'c_loadrunner',     # C: Loadrunner
        'caddcl',           # CAD DCL
        'cadlisp',          # CAD Lisp
        'cfdg',             # CFDG
        'chaiscript',       # ChaiScript
        'clojure',          # Clojure
        'klonec',           # Clone C
        'klonecpp',         # Clone C++
        'cmake',            # CMake
        'cobol',            # COBOL
        'coffeescript',     # CoffeeScript
        'cfm',              # ColdFusion
        'css',              # CSS
        'cuesheet',         # Cuesheet
        'd',                # D
        'dcs',              # DCS
        'delphi',           # Delphi
        'oxygene',          # Delphi Prism (Oxygene)
        'diff',             # Diff
        'div',              # DIV
        'dos',              # DOS
        'dot',              # DOT
        'e',                # E
        'ecmascript',       # ECMAScript
        'eiffel',           # Eiffel
        'email',            # Email
        'epc',              # EPC
        'erlang',           # Erlang
        'fsharp',           # F#
        'falcon',           # Falcon
        'fo',               # FO Language
        'f1',               # Formula One
        'fortran',          # Fortran
        'freebasic',        # FreeBasic
        'freeswitch',       # FreeSWITCH
        'gambas',           # GAMBAS
        'gml',              # Game Maker
        'gdb',              # GDB
        'genero',           # Genero
        'genie',            # Genie
        'gettext',          # GetText
        'go',               # Go
        'groovy',           # Groovy
        'gwbasic',          # GwBasic
        'haskell',          # Haskell
        'hicest',           # HicEst
        'hq9plus',          # HQ9 Plus
        'html4strict',      # HTML
        'html5',            # HTML 5
        'icon',             # Icon
        'idl',              # IDL
        'ini',              # INI file
        'inno',             # Inno Script
        'intercal',         # INTERCAL
        'io',               # IO
        'j',                # J
        'java',             # Java
        'java5',            # Java 5
        'javascript',       # JavaScript
        'jquery',           # jQuery
        'kixtart',          # KiXtart
        'latex',            # Latex
        'lb',               # Liberty BASIC
        'lsl2',             # Linden Scripting
        'lisp',             # Lisp
        'llvm',             # LLVM
        'locobasic',        # Loco Basic
        'logtalk',          # Logtalk
        'lolcode',          # LOL Code
        'lotusformulas',    # Lotus Formulas
        'lotusscript',      # Lotus Script
        'lscript',          # LScript
        'lua',              # Lua
        'm68k',             # M68000 Assembler
        'magiksf',          # MagikSF
        'make',             # Make
        'mapbasic',         # MapBasic
        'matlab',           # MatLab
        'mirc',             # mIRC
        'mmix',             # MIX Assembler
        'modula2',          # Modula 2
        'modula3',          # Modula 3
        '68000devpac',      # Motorola 68000 HiSoft Dev
        'mpasm',            # MPASM
        'mxml',             # MXML
        'mysql',            # MySQL
        'newlisp',          # newLISP
        'text',             # None
        'nsis',             # NullSoft Installer
        'oberon2',          # Oberon 2
        'objeck',           # Objeck Programming Langua
        'objc',             # Objective C
        'ocaml-brief',      # OCalm Brief
        'ocaml',            # OCaml
        'pf',               # OpenBSD PACKET FILTER
        'glsl',             # OpenGL Shading
        'oobas',            # Openoffice BASIC
        'oracle11',         # Oracle 11
        'oracle8',          # Oracle 8
        'oz',               # Oz
        'pascal',           # Pascal
        'pawn',             # PAWN
        'pcre',             # PCRE
        'per',              # Per
        'perl',             # Perl
        'perl6',            # Perl 6
        'php',              # PHP
        'php-brief',        # PHP Brief
        'pic16',            # Pic 16
        'pike',             # Pike
        'pixelbender',      # Pixel Bender
        'plsql',            # PL/SQL
        'postgresql',       # PostgreSQL
        'povray',           # POV-Ray
        'powershell',       # Power Shell
        'powerbuilder',     # PowerBuilder
        'proftpd',          # ProFTPd
        'progress',         # Progress
        'prolog',           # Prolog
        'properties',       # Properties
        'providex',         # ProvideX
        'purebasic',        # PureBasic
        'pycon',            # PyCon
        'python',           # Python
        'q',                # q/kdb+
        'qbasic',           # QBasic
        'rsplus',           # R
        'rails',            # Rails
        'rebol',            # REBOL
        'reg',              # REG
        'robots',           # Robots
        'rpmspec',          # RPM Spec
        'ruby',             # Ruby
        'gnuplot',          # Ruby Gnuplot
        'sas',              # SAS
        'scala',            # Scala
        'scheme',           # Scheme
        'scilab',           # Scilab
        'sdlbasic',         # SdlBasic
        'smalltalk',        # Smalltalk
        'smarty',           # Smarty
        'sql',              # SQL
        'systemverilog',    # SystemVerilog
        'tsql',             # T-SQL
        'tcl',              # TCL
        'teraterm',         # Tera Term
        'thinbasic',        # thinBasic
        'typoscript',       # TypoScript
        'unicon',           # Unicon
        'uscript',          # UnrealScript
        'vala',             # Vala
        'vbnet',            # VB.NET
        'verilog',          # VeriLog
        'vhdl',             # VHDL
        'vim',              # VIM
        'visualprolog',     # Visual Pro Log
        'vb',               # VisualBasic
        'visualfoxpro',     # VisualFoxPro
        'whitespace',       # WhiteSpace
        'whois',            # WHOIS
        'winbatch',         # Winbatch
        'xbasic',           # XBasic
        'xml',              # XML
        'xorg_conf',        # Xorg Config
        'xpp',              # XPP
        'yaml',             # YAML
        'z80',              # Z80 Assembler
        'zxbasic',          # ZXBasic
    )

    @classmethod
    def submit(cls, paste_code,
                paste_name = None, paste_private = None,
                paste_expire_date = None, paste_format = None):
        """
        Submit a code snippet to Pastebin.

        @type  paste_code: str
        @param paste_code: Code or text to send to U{http://pastebin.com}.

        @type  paste_name: str
        @param paste_name: (Optional) Name of the author of the paste.
            Default is to paste anonymously.

        @type  paste_private: bool
        @param paste_private: (Optional) C{True} if the paste is private (only
            visible with the link), C{False} if it's public (indexed and
            searchable). The Pastebin FAQ (U{http://pastebin.com/faq}) claims
            private pastes are not indexed by search engines (aka Google).

        @type  paste_expire_date: str
        @param paste_expire_date: (Optional) Expiration date for the paste.
            Once past this date the paste is deleted automatically. Valid
            values are found in the L{Pastebin.paste_expire_date} class member.
            If not provided, the paste never expires.

        @type  paste_format: str
        @param paste_format: (Optional) Programming language of the code being
            pasted. This enables syntax highlighting when reading the code in
            U{http://pastebin.com}. Default is no syntax highlighting (text is
            just text and not source code).

        @rtype:  str
        @return: Returns the URL to the newly created paste.

        @raise PastebinError: The Pastebin API has returned an error message.

        @raise IOError: An error occurred when contacting the Pastebin web
            application. This is typically caused by network errors.
        """

        # Code snippet to submit
        argv = { 'paste_code' : str(paste_code) }

        # Name of the poster
        if paste_name is not None:
            argv['paste_name'] = str(paste_name)

        # Is the snippet private?
        if paste_private is not None:
            argv['paste_private'] = int(bool(int(paste_private)))

        # Expiration for the snippet
        if paste_expire_date is not None:
            paste_expire_date = str(paste_expire_date).strip().upper()
            argv['paste_expire_date'] = paste_expire_date

        # Syntax highlighting
        if paste_format is not None:
            paste_format = str(paste_format).strip().lower()
            argv['paste_format'] = paste_format

        # Make the request to the Pastebin API
        fd = urllib.urlopen(cls._api_url, urllib.urlencode(argv))
        try:
            response = fd.read()
        finally:
            fd.close()
        del fd

        # Return the new snippet URL on success, raise exception on error
        if not response.startswith(cls._prefix_url):
            raise PastebinError(response)
        return response

# Simple interface.
submit = Pastebin.submit

if __name__ == "__main__":
    import sys
    import optparse

    # Build the command line parser
    parser = optparse.OptionParser(usage = '%prog <file> [options]')
    parser.add_option("-n", "--name",
                      action="store", type="string", metavar="NAME",
                      help="author of the code to submit")
    parser.add_option("--private",
                      action="store_true",
                      help="the snippet is private")
    parser.add_option("--public",
                      action="store_false", dest="private",
                      help="the snippet is public")
    parser.add_option("-e", "--expire",
                      action="store", type="string", metavar="TIME",
                      help="expiration time: N (never), 10M (10 minutes), 1H (1 hour), 1D (1 day), 1M (1 month)")
    parser.add_option("-f", "--format", "--syntax", "--highlight",
                      action="store", type="string", metavar="FORMAT", dest="format",
                      help="syntax highlighting, use one of the following: " + \
                           ', '.join(Pastebin.paste_format))

    # Parse the command line and submit each snippet
    options, args = parser.parse_args(sys.argv)
    args = args[1:]
    if not args:
        parser.print_help()
    for filename in args:
        data = open(filename, 'rb').read()
        url = Pastebin.submit(paste_code = data,
                              paste_name = options.name,
                              paste_private = options.private,
                              paste_expire_date = options.expire,
                              paste_format = options.format)
        print "%s --> %s" % (filename, url)
