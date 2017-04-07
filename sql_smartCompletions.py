#built by: @asopenag on April 2017
#version: 0.1.0

import re

import sublime
import sublime_plugin

from asopenag_plugins.sql_smart_completions.asopenag_columns_file import *   #import columns file

columns_in_lowercase = sublime.load_settings('sql_smartCompletions.sublime-settings').get('columns_in_lowercase')  #read property

class AutoCompleteListener(sublime_plugin.EventListener):
    print("Use lower: " + str(columns_in_lowercase))

    # --------------------- Main funciton, called on query completions ---------------------
    def on_query_completions(self, view, prefix, locations):
        print("------") 
        #1. Check current scope (only apply this to SQL scope)
        loc = locations[0]
        if not view.score_selector(loc, "source.sql"):
            return

        #2. Get texts to use
        line_after_cursor = view.substr(sublime.Region(loc, view.line(loc).b))
        line_before_cursor = view.substr(sublime.Region(loc, view.line(loc).a))

        all_view_text = view.substr(sublime.Region(0, view.size()))


        #3. Find table full name from table short name
        mTableFullName = self.getTableNameIfAny(line_before_cursor, all_view_text)

        if mTableFullName == None:
            return


        #4. Get the columns for that Table
        tableColumns = self.getTableColumns(mTableFullName)

        return ( 
            tableColumns,
            sublime.INHIBIT_WORD_COMPLETIONS + sublime.INHIBIT_EXPLICIT_COMPLETIONS #remove all other completions (context based and completion-files based)
        )


    # --------------------- Get table full name from the code (using its declaration) [this retunrs the latest match if more than one...] ---------------------
    def getTableNameIfAny(self, aLineBefore, aFullFileText):
        table_alias = ""
        table_full_name = ""

        #1. Find table short name:
        for (matchh) in re.findall('([\w\d]+)\.\w*$', aLineBefore, re.IGNORECASE):
            table_alias = matchh

        if table_alias == "":
            return None

        #2. Get table full name (based on short_name declaration)_
        patternn = '([\w\d]+) +( *as +)?' + table_alias + '(\n| |-|\t)'  #table name, table short name, characters ending the short name (mandatory to avoid similar words starting with shortname) | assume "as" can be used TABLE as tablee
        #print("pattern: " + patternn)
        for (tables_match, aux_second_group, aux_third_group) in re.findall(patternn, aFullFileText, re.IGNORECASE):
            print("Table full name: "+ tables_match)
            table_full_name = tables_match

        print("table short name: " + table_alias)

        #3. Return full table name:
        return table_full_name


    #--------------------- Get the Columns of this specific Table ---------------------
    def getTableColumns(self, aTableName):
        # return [
        #     ("propertyA_a\tmyClass", "property_Aa"),
        #     ("propertyA_b\tmyClass", "property_Ab"),
        #     ("propertyA_c\tmyClass", "property_Ac")
        # ]

        #1. Get columns from columns file 
        completionss = mColumnsDictionary.get(aTableName.upper(), "notfound")

        #if not found, return empty array
        if completionss == "notfound":
            print("No columns found for this table")
            completionss = []

        #2. Check if user prefers lower or upper cases
        if not columns_in_lowercase:
            print("columns format: uppercase")
            return completionss
        else:
            print("columns format: lowercase")
            completionss = [[j.lower() for j in i] for i in completionss]
            return completionss