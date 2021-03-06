# -*- coding: utf-8 -*-
"""Setup the tracim application"""
from __future__ import print_function

import logging
from tg import config
import transaction

def setup_schema(command, conf, vars):
    """Place any commands to setup tracim here"""
    # Load the models

    # <websetup.websetup.schema.before.model.import>
    from tracim import model
    # <websetup.websetup.schema.after.model.import>

    
    # <websetup.websetup.schema.before.metadata.create_all>
    print("Creating tables")
    # model.metadata.create_all(bind=config['tg.app_globals'].sa_engine)

    # result = config['tg.app_globals'].sa_engine.execute(get_initial_schema())
    from sqlalchemy import DDL
    result = model.DBSession.execute(DDL(get_initial_schema()))
    print("Initial schema created.")

    #ALTER TABLE bibi ADD COLUMN popo integer;

    # <websetup.websetup.schema.after.metadata.create_all>
    transaction.commit()
    print('Initializing Migrations')
    import alembic.config, alembic.command
    alembic_cfg = alembic.config.Config()
    alembic_cfg.set_main_option("script_location", "migration")
    alembic_cfg.set_main_option("sqlalchemy.url", config['sqlalchemy.url'])
    alembic.command.stamp(alembic_cfg, "head")


def get_initial_schema():
    return """
SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

-- CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;
-- COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';
SET search_path = public, pg_catalog;


CREATE OR REPLACE FUNCTION update_node() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
INSERT INTO content_revisions (content_id, parent_id, type, created, updated,
       label, description, status,
       file_name, file_content, file_mimetype,
       owner_id, revision_id, workspace_id, is_deleted, is_archived, properties, revision_type) VALUES (NEW.content_id, NEW.parent_id, NEW.type, NEW.created, NEW.updated, NEW.label, NEW.description, NEW.status, NEW.file_name, NEW.file_content, NEW.file_mimetype, NEW.owner_id, nextval('seq__content_revisions__revision_id'), NEW.workspace_id, NEW.is_deleted, NEW.is_archived, NEW.properties, NEW.revision_type);
return new;
END;
$$;

CREATE OR REPLACE FUNCTION set_created() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.created = CURRENT_TIMESTAMP;
    NEW.updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

CREATE OR REPLACE FUNCTION set_updated() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;

SET default_tablespace = '';
SET default_with_oids = false;

-- CREATE TABLE migrate_version (
--    version_num character varying(32) NOT NULL
-- );

CREATE TABLE groups (
    group_id integer NOT NULL,
    group_name character varying(16) NOT NULL,
    display_name character varying(255),
    created timestamp without time zone
);

CREATE SEQUENCE seq__groups__group_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE seq__groups__group_id OWNED BY groups.group_id;

CREATE TABLE group_permission (
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);

CREATE SEQUENCE seq__content_revisions__revision_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE content_revisions (
    content_id integer NOT NULL,
    parent_id integer,
    type character varying(16) DEFAULT 'data'::character varying NOT NULL,
    created timestamp without time zone,
    updated timestamp without time zone,
    label character varying(1024),
    description text DEFAULT ''::text NOT NULL,
    status character varying(32) DEFAULT 'new'::character varying,
    file_name character varying(255),
    file_content bytea,
    file_mimetype character varying(255),
    owner_id integer,
    revision_id integer DEFAULT nextval('seq__content_revisions__revision_id'::regclass) NOT NULL,
    workspace_id integer,
    is_deleted boolean DEFAULT false NOT NULL,
    is_archived boolean DEFAULT false NOT NULL,
    properties text,
    revision_type character varying(32)
);

COMMENT ON COLUMN content_revisions.properties IS 'This column contain properties specific to a given type. these properties are json encoded (so there is no structure "a priori")';

CREATE VIEW contents AS
    SELECT DISTINCT ON (content_revisions.content_id) content_revisions.content_id, content_revisions.parent_id, content_revisions.type, content_revisions.created, content_revisions.updated, content_revisions.label, content_revisions.description, content_revisions.status, content_revisions.file_name, content_revisions.file_content, content_revisions.file_mimetype, content_revisions.owner_id, content_revisions.workspace_id, content_revisions.is_deleted, content_revisions.is_archived, content_revisions.properties, content_revisions.revision_type FROM content_revisions ORDER BY content_revisions.content_id, content_revisions.updated DESC, content_revisions.created DESC;

CREATE SEQUENCE seq__contents__content_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE seq__contents__content_id OWNED BY content_revisions.content_id;

CREATE TABLE permissions (
    permission_id integer NOT NULL,
    permission_name character varying(63) NOT NULL,
    description character varying(255)
);

CREATE SEQUENCE seq__permissions__permission_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE seq__permissions__permission_id OWNED BY permissions.permission_id;

CREATE TABLE users (
    user_id integer NOT NULL,
    email character varying(255) NOT NULL,
    display_name character varying(255),
    password character varying(128),
    created timestamp without time zone,
    is_active boolean DEFAULT true NOT NULL
);

CREATE TABLE user_group (
    user_id integer NOT NULL,
    group_id integer NOT NULL
);

CREATE SEQUENCE seq__users__user_id
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER SEQUENCE seq__users__user_id OWNED BY users.user_id;

CREATE TABLE user_workspace (
    user_id integer NOT NULL,
    workspace_id integer NOT NULL,
    role integer,
    do_notify boolean DEFAULT FALSE NOT NULL
);

CREATE TABLE workspaces (
    workspace_id integer NOT NULL,
    label character varying(1024),
    description text,
    created timestamp without time zone,
    updated timestamp without time zone,
    is_deleted boolean DEFAULT false NOT NULL
);

CREATE SEQUENCE seq__workspaces__workspace_id
    START WITH 11
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE ONLY groups ALTER COLUMN group_id SET DEFAULT nextval('seq__groups__group_id'::regclass);
ALTER TABLE ONLY content_revisions ALTER COLUMN content_id SET DEFAULT nextval('seq__contents__content_id'::regclass);
ALTER TABLE ONLY permissions ALTER COLUMN permission_id SET DEFAULT nextval('seq__permissions__permission_id'::regclass);
ALTER TABLE ONLY users ALTER COLUMN user_id SET DEFAULT nextval('seq__users__user_id'::regclass);
ALTER TABLE ONLY workspaces ALTER COLUMN workspace_id SET DEFAULT nextval('seq__workspaces__workspace_id'::regclass);

-- COPY migrate_version (version_num) FROM stdin;

SELECT pg_catalog.setval('seq__groups__group_id', 4, true);
SELECT pg_catalog.setval('seq__contents__content_id', 1, true);
SELECT pg_catalog.setval('seq__content_revisions__revision_id', 2568, true);
SELECT pg_catalog.setval('seq__permissions__permission_id', 1, true);
SELECT pg_catalog.setval('seq__users__user_id', 2, true);

SELECT pg_catalog.setval('seq__workspaces__workspace_id', 1, true);

ALTER TABLE ONLY user_workspace
    ADD CONSTRAINT pk__user_workspace__user_id__workspace_id PRIMARY KEY (user_id, workspace_id);

ALTER TABLE ONLY workspaces
    ADD CONSTRAINT pk__workspace__workspace_id PRIMARY KEY (workspace_id);

ALTER TABLE ONLY groups
    ADD CONSTRAINT uk__groups__group_name UNIQUE (group_name);

ALTER TABLE ONLY group_permission
    ADD CONSTRAINT pk__group_permission__group_id__permission_id PRIMARY KEY (group_id, permission_id);

ALTER TABLE ONLY groups
    ADD CONSTRAINT pk__groups__group_id PRIMARY KEY (group_id);

ALTER TABLE ONLY content_revisions
    ADD CONSTRAINT pk__content_revisions__revision_id PRIMARY KEY (revision_id);

ALTER TABLE ONLY permissions
    ADD CONSTRAINT uk__permissions__permission_name UNIQUE (permission_name);

ALTER TABLE ONLY permissions
    ADD CONSTRAINT pk__permissions__permission_id PRIMARY KEY (permission_id);

ALTER TABLE ONLY users
    ADD CONSTRAINT uk__users__email UNIQUE (email);

ALTER TABLE ONLY user_group
    ADD CONSTRAINT pk__user_group__user_id__group_id PRIMARY KEY (user_id, group_id);

ALTER TABLE ONLY users
    ADD CONSTRAINT pk__users__user_id PRIMARY KEY (user_id);

CREATE INDEX idx__content_revisions__owner_id ON content_revisions USING btree (owner_id);

CREATE INDEX idx__content_revisions__parent_id ON content_revisions USING btree (parent_id);

CREATE RULE rul__insert__new_node AS ON INSERT TO contents DO INSTEAD INSERT INTO content_revisions (content_id, parent_id, type, created, updated, label, description, status, file_name, file_content, file_mimetype, owner_id, revision_id, workspace_id, is_deleted, is_archived, properties, revision_type) VALUES (nextval('seq__contents__content_id'::regclass), new.parent_id, new.type, new.created, new.updated, new.label, new.description, new.status, new.file_name, new.file_content, new.file_mimetype, new.owner_id, nextval('seq__content_revisions__revision_id'::regclass), new.workspace_id, new.is_deleted, new.is_archived, new.properties, new.revision_type) RETURNING content_revisions.content_id, content_revisions.parent_id, content_revisions.type, content_revisions.created, content_revisions.updated, content_revisions.label, content_revisions.description, content_revisions.status, content_revisions.file_name, content_revisions.file_content, content_revisions.file_mimetype, content_revisions.owner_id, content_revisions.workspace_id, content_revisions.is_deleted, content_revisions.is_archived, content_revisions.properties, content_revisions.revision_type;

CREATE TRIGGER trg__contents__on_insert__set_created BEFORE INSERT ON content_revisions FOR EACH ROW EXECUTE PROCEDURE set_created();
CREATE TRIGGER trg__contents__on_update__set_updated BEFORE UPDATE ON content_revisions FOR EACH ROW EXECUTE PROCEDURE set_updated();

CREATE TRIGGER trg__contents__on_update INSTEAD OF UPDATE ON contents FOR EACH ROW EXECUTE PROCEDURE update_node();
CREATE TRIGGER trg__workspaces__on_insert__set_created BEFORE INSERT ON workspaces FOR EACH ROW EXECUTE PROCEDURE set_created();
CREATE TRIGGER trg__workspaces__on_update__set_updated BEFORE UPDATE ON workspaces FOR EACH ROW EXECUTE PROCEDURE set_updated();

ALTER TABLE ONLY user_workspace
    ADD CONSTRAINT fk__user_workspace__user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY user_workspace
    ADD CONSTRAINT fk__user_workspace__workspace_id FOREIGN KEY (workspace_id) REFERENCES workspaces(workspace_id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY group_permission
    ADD CONSTRAINT fk__group_permission__group_id FOREIGN KEY (group_id) REFERENCES groups(group_id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY group_permission
    ADD CONSTRAINT fk__group_permission__permission_id FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY content_revisions
    ADD CONSTRAINT fk__content_revisions__owner_id FOREIGN KEY (owner_id) REFERENCES users(user_id);

ALTER TABLE ONLY user_group
    ADD CONSTRAINT fk__user_group__group_id FOREIGN KEY (group_id) REFERENCES groups(group_id) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE ONLY user_group
    ADD CONSTRAINT fk__user_group__user_id FOREIGN KEY (user_id) REFERENCES users(user_id) ON UPDATE CASCADE ON DELETE CASCADE;

COMMIT;
"""