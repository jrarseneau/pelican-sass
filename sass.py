# -*- coding: utf-8 -*-
"""
Pelican plugin to implement libsass. Autocompiles your SASS
files during every regeneration.

"""
import os, io
import json
import logging
from pelican import signals
import sass

def write_content(content, destination):
        """
        Write given content to destination path.
        It will create needed directory structure first if it contain some
        directories that does not allready exists.
        Args:
            content (str): Content to write to target file.
            destination (str): Destination path for target file.
        Returns:
            str: Path where target file has been written.
        """
        try:
            directory = os.path.dirname(destination)

            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            with io.open(destination, 'w', encoding='utf-8') as f:
                f.write(content)

        except Exception as e:
            print(e)
        
        CGREEN  = '\33[32m'
        CEND = '\033[0m'
        print(CGREEN + "pelican-sass: Generating output: %s" % destination + CEND)

def sass_compile(file, destination, output_style, source_comments):
    
    try:
        content = sass.compile(
                filename=file,
                output_style=output_style,
                source_comments=source_comments,
                # include_paths=settings.LIBRARY_PATHS,
                # Sourcemap is allways in the same directory than compiled
                # CSS file
                #output_filename_hint='',
                #source_map_filename=source_map_destination,
            )

    except Exception as e:
        print(e)
    
    # Write our content
    base = os.path.basename(file)
    dest_file = "%s/%s.css" % (destination, os.path.splitext(base)[0])
    write_content(content, dest_file)

def _load_settings(file):
    global settings
    
    with open(file) as f:
        settings = json.load(f)
    
    # Make sure all supported keys exist in settings.json
    if 'SOURCES_PATH' not in settings:
        raise ValueError('pelican-sass: SOURCE_PATH key mmissing in settings.json')
    if 'TARGET_PATH' not in settings:
        raise ValueError('pelican-sass: TARGET_PATH key missing in settings.json')
    if 'OUTPUT_STYLES' not in settings:
        print("pelican-sass: OUTPUT_STYLES key missing in settings.json, defaulting to 'nested'")
        settings['OUTPUT_STYLES'] = 'nested'
    if 'SOURCE_COMMENTS' not in settings:
        print("pelican-sass: SOURCE_COMMENTS key missing in settings.json, defaulting to false")
        settings['SOURCE_COMMENTS'] = False        


def initialize(pelicanobj):
    """Add libsass compilation to Pelican."""

    # Load 'settings.json' from the root theme folder
    settings_file = "%s/settings.json" % pelicanobj.settings.get('THEME', None)

    if os.path.isfile(settings_file):
        _load_settings(settings_file)
    else:
        raise ValueError("pelican-sass error: %s does not exist." % settings_file)
    
    # Shorten our SOURCES_PATH and TARGET_PATH
    SOURCES_PATH = "%s/%s" % (pelicanobj.settings.get('THEME', None), settings['SOURCES_PATH'])
    TARGET_PATH = "%s/%s" % (pelicanobj.settings.get('THEME', None), settings['TARGET_PATH'])

    # Ensure SOURCES_PATH and TARGET_DIR are folders
    if not os.path.isdir(SOURCES_PATH):
        raise ValueError("pelican-sass: SOURCES_PATH is not a valid folder.")

    for filename in os.listdir(SOURCES_PATH):
        if filename.endswith(".sass") or filename.endswith(".scss"):
            sass_compile(
                "%s/%s" % (SOURCES_PATH, filename), 
                TARGET_PATH,
                settings['OUTPUT_STYLES'], 
                settings['SOURCE_COMMENTS']
                )

def register():
    """Plugin registration."""
    print("Registering Pelican Libsass plugin by Jean-Ray Arseneau (https://theint.net/)")
    signals.static_generator_init.connect(initialize)