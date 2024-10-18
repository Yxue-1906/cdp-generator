import json
import argparse
import os.path
import re
import sys

import jinja2


class Protocol:
    domains = {}
    protocol = {}
    types = {}
    raw_types = {}

    def __init__(self, protocol_path):
        self.protocol = json.load(open(protocol_path, "r"))
        self.init_works()
        self.create_types()
        self.create_commands()
        self.create_events()

    def create_attr(self, domain, raw):
        base = {
            "name": raw["name"],
            "description": raw.get("description", ""),
            "domain": domain["domain"],
            "optional": raw.get("optional", False)
        }
        if "$ref" in raw:
            base["type"] = self.types[raw["$ref"]]
        elif raw["type"] != "array":
            base["type"] = self.types[raw["type"]]
        else:
            base["is_array"] = True
            item = raw["items"]
            if "$ref" in item:
                base["type"] = self.types[item["$ref"]]
            else:
                base["type"] = self.types[item["type"]]
        return base

    def create_commands(self):
        for domain in self.protocol["domains"]:
            for raw_command in domain["commands"]:
                command = {
                    "name": raw_command["name"],
                    "description": raw_command.get("description", ""),
                    "params": [],
                    "response": []
                }
                if "redirect" in raw_command:
                    # todo: we delete this command for now
                    continue

                for raw_param in raw_command.get("parameters", []):
                    command["params"].append(self.create_attr(domain, raw_param))
                for raw_response in raw_command.get("returns", []):
                    command["response"].append(self.create_attr(domain, raw_response))

                self.domains[domain["domain"]]["command_types"].append(command)

    def create_events(self):
        for domain in self.protocol["domains"]:
            for raw_event in domain.get("events", []):
                event = {
                    "name": raw_event["name"],
                    "description": raw_event.get("description", ""),
                    "attributes": []
                }

                for raw_attr in raw_event.get("parameters", []):
                    event["attributes"].append(self.create_attr(domain, raw_attr))

                self.domains[domain["domain"]]["event_types"].append(event)

    def create_types(self, ):
        for key, value in self.raw_types.items():
            if key in self.types:
                continue
            self.do_create_type(key)

    def do_create_type(self, search_name):
        if search_name in self.types:
            return
        raw_type = self.raw_types[search_name]
        domain_name = search_name.split('.')[0]
        type_base = {
            "name": raw_type["id"],
            "qualified_name": search_name.replace('.', "::"),
            "domain": domain_name,
            "description": raw_type.get("description", "")
        }
        self.types[search_name] = type_base
        if "enums" in raw_type:
            self.create_enum_type(type_base, raw_type)
            self.domains[domain_name]["enum_types"].append(type_base)
        elif raw_type["type"] == "object" and "properties" in raw_type:
            self.create_object_type(type_base, raw_type)
            self.domains[domain_name]["object_types"].append(type_base)
        elif raw_type["type"] == "array":
            self.create_array_type(type_base, raw_type)
            self.domains[domain_name]["using_types"].append({
                "name": raw_type["id"],
                "type": type_base["using"]
            })
        else:
            self.create_using_type(type_base, raw_type)
            self.domains[domain_name]["using_types"].append({
                "name": raw_type["id"],
                "type": type_base["using"]
            })
            self.types[search_name] = type_base["using"]

    def create_enum_type(self, base, raw):
        base["name"] += "Enum"
        base["qualified_name"] += "Enum"
        base["enums"] = raw["enum"]

    def create_object_type(self, base, raw):
        raw_properties = raw["properties"]
        properties = []
        base["properties"] = properties

        for raw_property in raw_properties:
            property_base = {
                "name": raw_property["name"],
                "description": raw_property.get("description", ""),
                "domain": base["domain"],
                "optional": raw_property.get("optional", False)
            }
            if "$ref" in raw_property:
                self.do_create_type(raw_property["$ref"])
                property_base["type"] = self.types[raw_property["$ref"]]
            elif "enum" in raw_property:
                property_enum_type_name = raw_property["name"] + "Enum"
                property_enum_type = {
                    "name": property_enum_type_name,
                    "qualified_name": "{}::{}::{}".format(base["domain"], base["name"], property_enum_type_name),
                    "domain": base["domain"],
                    "enums": raw_property["enum"]
                }
                self.domains[base["domain"]]["enum_types"].append(property_enum_type)
                property_base["type"] = property_enum_type
                property_base["is_enum"] = True
            elif raw_property["type"] == "array":
                property_base["is_array"] = True
                array_item = raw_property["items"]
                if "$ref" in array_item:
                    self.do_create_type(array_item["$ref"])
                    property_base["type"] = self.types[array_item["$ref"]]
                else:
                    property_base["type"] = self.types[array_item["type"]]
            else:
                property_base["type"] = self.types[raw_property["type"]]

            properties.append(property_base)

    def create_array_type(self, base, raw):
        item = raw["items"]
        if "$ref" in item:
            self.do_create_type(item["$ref"])
            item = self.types[item["$ref"]]
        else:
            item = self.types[item["type"]]
        using_type = item | {
            "name": "Array<{}>".format(item["name"]),
            "qualified_name": "Array<{}>".format(item["qualified_name"])
        }
        base["using"] = using_type

    def create_using_type(self, base, raw_type):
        base["using"] = self.types[raw_type["type"]]

    def init_works(self):
        # init builtin types
        for t in ["number", "string", "integer", "boolean", "any", "object"]:
            if t == "any" or t == "object":
                self.types[t] = {
                    "name": "Any",
                    "qualified_name": "Any",
                    "type": "Ptr<Any>",
                    "qualified_type": "Ptr<Any>"
                }
            else:
                self.types[t] = {
                    "name": t.capitalize(),
                    "qualified_name": t.capitalize(),
                    "type": f"Ptr<{t.capitalize()}>",
                    "qualified_type": f"Ptr<{t.capitalize()}>"
                }
        # init domains
        for domain in self.protocol["domains"]:
            self.domains[domain["domain"]] = {
                "domain": domain["domain"],
                "description": domain.get("description", ""),
                "enum_types": [],
                "using_types": [],
                "object_types": [],
                "event_types": [],
                "command_types": [],
                "dependencies": domain.get("dependencies", [])
            }

        # init raw types
        for domain in self.protocol["domains"]:
            for t in domain.get("types", {}):
                search_name = domain["domain"] + "." + t["id"]
                self.raw_types[search_name] = t

            # qualify ref name
            def qualify_name(j):
                if isinstance(j, list):
                    for item in j:
                        qualify_name(item)
                if not isinstance(j, dict):
                    return
                for k, v in j.items():
                    if k == "$ref":
                        if '.' not in v:
                            j[k] = domain["domain"] + '.' + v
                    else:
                        qualify_name(v)

            qualify_name(domain)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", type=str, nargs='+', default=[])
    parser.add_argument("--templates", type=str, required=True, help="directory where templates locate")
    parser.add_argument("--output", type=str, required=True, help="directory where outputs locate")
    parser.add_argument("--protocol", type=str, required=True, help="path to protocol in json")

    args = parser.parse_args()

    protocol = Protocol(args.protocol)

    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(args.templates),
        keep_trailing_newline=True,
        lstrip_blocks=True,
        trim_blocks=True
    )

    def to_title_case(name):
        return name[:1].upper() + name[1:]

    def dash_to_camelcase(word):
        prefix = ""
        if word[0] == "-":
            prefix = "Negative"
            word = word[1:]
        return prefix + "".join(to_title_case(x) or "-" for x in word.split("-"))

    def to_snake_case(name):
        name = re.sub(r"([A-Z]{2,})([A-Z][a-z])", r"\1_\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name, sys.maxsize).lower()

    def to_array_type(type):
        return "Array<{}>".format(type)

    def format_include(name):
        if not name.endswith(".h"):
            name = name + ".h"
        if name[0] not in "\"<":
            name = "\"" + name + "\""
        return name

    def wrap_ptr(name):
        return "Ptr<{}>".format(name)

    jinja_env.filters.update({
        "to_title_case": to_title_case,
        "dash_to_camelcase": dash_to_camelcase,
        "to_method_case": to_title_case,
        "to_snake_case": to_snake_case,
        "format_include": format_include,
        "to_array_type": to_array_type,
        "wrap_ptr": wrap_ptr
    })
    jinja_env.add_extension("jinja2.ext.loopcontrols")

    h_template = jinja_env.get_template("Type_h.template")
    cpp_template = jinja_env.get_template("Type_cpp.template")

    def write_to_file(path, content):
        with open(path, "a"):
            pass # insure file exist
        with open(path, "r") as f:
            old_content = f.read()
            if content == old_content:
                return
        with open(path, "w") as f:
            f.write(content)

    for k, v in protocol.domains.items():
        context = {
            "namespaces": args.namespace,
            "domain": v,
            "to_array_type": to_array_type,
            "dash_to_camelcase": dash_to_camelcase,
            "wrap_ptr": wrap_ptr
        }
        write_to_file(os.path.join(args.output, v["domain"] + ".h"), h_template.render(context))
        write_to_file(os.path.join(args.output, v["domain"] + ".cpp"), cpp_template.render(context))

    write_to_file(os.path.join(args.output, "Devtools.h"), jinja_env.get_template("Devtools_h.template").render({
        "namespaces": args.namespace
    }))
    write_to_file(os.path.join(args.output, "Devtools.cpp"), jinja_env.get_template("Devtools_cpp.template").render({
        "domains": protocol.domains,
        "namespaces": args.namespace,
        "dash_to_camelcase": dash_to_camelcase
    }))


if __name__ == "__main__":
    main()
