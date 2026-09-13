BEGIN;
-- limpieza previa

DROP TRIGGER IF EXISTS tg_auditoria_rol ON rol;
DROP TRIGGER IF EXISTS tg_auditoria_categoria ON categoria;
DROP TRIGGER IF EXISTS tg_auditoria_dificultad ON dificultad;
DROP TRIGGER IF EXISTS tg_auditoria_modo_puntaje ON modo_puntaje;
DROP TRIGGER IF EXISTS tg_auditoria_modalidad ON modalidad;
DROP TRIGGER IF EXISTS tg_auditoria_estado_inscripcion ON estado_inscripcion;
DROP TRIGGER IF EXISTS tg_auditoria_metodo_auth ON metodo_auth;
DROP TRIGGER IF EXISTS tg_auditoria_usuario ON usuario;
DROP TRIGGER IF EXISTS tg_auditoria_evento ON evento;
DROP TRIGGER IF EXISTS tg_auditoria_reto ON reto;
DROP TRIGGER IF EXISTS tg_auditoria_pista ON pista;
DROP TRIGGER IF EXISTS tg_auditoria_participa ON participa;
DROP TRIGGER IF EXISTS tg_auditoria_contiene ON contiene;

-- funcion auditoria
CREATE OR REPLACE FUNCTION fn_auditoria() RETURNS TRIGGER
LANGUAGE plpgsql
AS $$ 
DECLARE
	v_pk		TEXT := TG_ARGV[0];
	v_sencible	TEXT[] := CASE WHEN TG_NARGS > 1 AND TG_ARGV[1] <> ''
							THEN string_to_array(TG_ARGV[1], ',') ELSE '{}'::TEXT[] END;
	v_ignorar	TEXT[] := CASE WHEN TG_NARGS > 2 AND TG_ARGV[2] <> ''
							THEN string_to_array(TG_ARGV[2], ',') ELSE '{}'::TEXT[] END;
	v_antes		JSONB;
	v_despues	JSONB;
	v_campos	TEXT[];
	v_id		INTEGER;
	v_usuario 	INTEGER;
	c			TEXT;

BEGIN

	v_usuario := NULLIF(current_setting('app.id_usuario', true), '')::INTEGER;
	
	IF TG_OP <> 'INSERT' THEN v_antes := to_jsonb(OLD); END IF;
	IF TG_OP <> 'DELETE' THEN v_despues := to_jsonb(NEW); END IF;

	v_id := COALESCE(v_despues ->> v_pk, v_antes ->> v_pk)::INTEGER;

	IF TG_OP = 'UPDATE' THEN
		SELECT array_agg(d.k) INTO v_campos
		FROM jsonb_each(v_despues) AS d(k, v)
		WHERE d.v IS DISTINCT FROM (v_antes -> d.k)
			AND NOT (d.k = ANY (v_ignorar));

			IF v_campos IS NULL THEN
			RETURN NULL;

			END IF;
	END IF;

	FOREACH c IN ARRAY v_sencible LOOP
		IF jsonb_exists(v_antes, c) THEN v_antes := jsonb_set(v_antes, ARRAY[c],'"***"'); END IF;
		IF jsonb_exists(v_despues, c) THEN v_despues := jsonb_set(v_despues, ARRAY[c],'"***"'); END IF;
	END LOOP;

	INSERT INTO auditoria (tabla, id_registro, operacion, id_usuario, datos_antes, datos_despues, campos)
	VALUES(TG_TABLE_NAME, v_id, TG_OP, v_usuario, v_antes, v_despues, v_campos);

	RETURN NULL;
END;
$$;



-- triggers tb catalogos
CREATE TRIGGER tg_auditoria_rol AFTER INSERT OR UPDATE OR DELETE ON rol 
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_rol', '', '');
CREATE TRIGGER tg_auditoria_categoria AFTER INSERT OR UPDATE OR DELETE ON categoria
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_categoria', '', '');
CREATE TRIGGER tg_auditoria_dificultad AFTER INSERT OR UPDATE OR DELETE ON dificultad 
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_dificultad', '', '');
CREATE TRIGGER tg_auditoria_modo_puntaje AFTER INSERT OR UPDATE OR DELETE ON modo_puntaje 
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_modo_puntaje', '', '');
CREATE TRIGGER tg_auditoria_modalidad AFTER INSERT OR UPDATE OR DELETE ON modalidad
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_modalidad', '', '');
CREATE TRIGGER tg_auditoria_estado_inscripcion AFTER INSERT OR UPDATE OR DELETE ON estado_inscripcion
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_estado_inscripcion', '', '');
CREATE TRIGGER tg_auditoria_metodo_auth AFTER INSERT OR UPDATE OR DELETE ON metodo_auth
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_metodo_auth', '', '');
-- trigers tb entidades
CREATE TRIGGER tg_auditoria_usuario AFTER INSERT OR UPDATE OR DELETE ON usuario
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_usuario', 'password_hash', '');
CREATE TRIGGER tg_auditoria_evento AFTER INSERT OR UPDATE OR DELETE ON evento
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_evento', '', '');
CREATE TRIGGER tg_auditoria_reto AFTER INSERT OR UPDATE OR DELETE ON reto
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_reto', 'flag', '');
CREATE TRIGGER tg_auditoria_pista AFTER INSERT OR UPDATE OR DELETE ON pista 
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_pista', '', '');
-- trigger tb asosiativas
CREATE TRIGGER tg_auditoria_participa AFTER INSERT OR UPDATE OR DELETE ON participa 
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_participa', '', '');
CREATE TRIGGER tg_auditoria_contiene AFTER INSERT OR UPDATE OR DELETE ON contiene
	FOR EACH ROW EXECUTE FUNCTION fn_auditoria('id_contiene', '', 'puntaje_actual');
COMMIT;