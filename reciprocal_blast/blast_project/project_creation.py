from django.db import IntegrityError, transaction

from .blast_execution import write_snakefile, write_nr_snakefile
from .services import save_genomes_and_query_in_db, save_project_from_form_or_raise_exception, \
    upload_file, create_project_dir, \
    save_forward_settings_from_form_or_raise_exception, save_backward_settings_from_form_or_raise_exception, \
    save_nr_project_from_form_or_raise_exception, save_query_file_in_db, \
    create_nr_project_dir, validate_fw_taxids_and_save_into_database, validate_bw_taxids_and_save_into_database


def create_project_with_previously_uploaded_genomes(request, project_creation_form,settings_form_forward,settings_form_backward):

    try:
        # ensures that everything is correctly saved into the database, if an error occurres saving would not be transmitted
        with transaction.atomic():
            new_title = project_creation_form.cleaned_data['project_title']
            new_strategy = project_creation_form.cleaned_data['search_strategy']
            project = save_project_from_form_or_raise_exception(new_title, new_strategy, request.user)

            forward_genome = project_creation_form.cleaned_data['forward_genome_file']
            backward_genome = project_creation_form.cleaned_data['backward_genome_file']

            # just the genome/database name is required in order to reuse this object
            forward_genome_data = Genomes.objects.filter(genome_name=forward_genome).order_by('id').first()
            backward_genome_data = Genomes.objects.filter(genome_name=backward_genome).order_by('id').first()

            query_sequences = request.FILES['query_sequence_file']

            create_project_dir(project)
            upload_file(query_sequences,
                        'media/' + str(project.id) + '/' + 'query_sequences' + '/' + query_sequences.name)
            save_genomes_and_query_in_db(query_sequences, forward_genome_data.genome_name,
                                         backward_genome_data.genome_name, project)

            save_forward_settings_from_form_or_raise_exception(project, settings_form_forward.cleaned_data)
            save_backward_settings_from_form_or_raise_exception(project, settings_form_backward.cleaned_data)
            write_snakefile(project.id)

    except Exception as e:
        raise IntegrityError("[-] Couldn't perform project creation due to exception: {}".format(e))

def create_project_with_nr_database(request, project_creation_form,settings_form_forward,settings_form_backward):
    try:
        # ensures that everything is correctly saved into the database, if an error occurres saving would not be transmitted
        with transaction.atomic():
            new_title = project_creation_form.cleaned_data['project_title']
            taxonomic_nodes_bw = project_creation_form.cleaned_data['taxid_bw']
            taxonomic_nodes_fw = project_creation_form.cleaned_data['taxid_fw']
            query_sequences = request.FILES['query_sequence_file']

            project = save_nr_project_from_form_or_raise_exception(new_title, request.user)

            validate_fw_taxids_and_save_into_database(project, request.user.email, taxonomic_nodes_fw)
            validate_bw_taxids_and_save_into_database(project, request.user.email, taxonomic_nodes_bw)

            save_query_file_in_db(query_sequences, project)

            save_forward_settings_from_form_or_raise_exception(project, settings_form_forward.cleaned_data)
            save_backward_settings_from_form_or_raise_exception(project,
                                                                settings_form_backward.cleaned_data)

            create_nr_project_dir(project)
            upload_file(query_sequences,
                        'media/' + str(project.id) + '/' + 'query_sequences' + '/' + query_sequences.name)

            write_nr_snakefile(project.id)
    except Exception as e:
        raise IntegrityError("[-] Couldn't perform project creation due to exception: {}".format(e))

def create_project_with_uploaded_files(request, project_creation_form,settings_form_forward,settings_form_backward):
    try:
        # ensures that everything is correctly saved into the database, if an error occurres saving would not be transmitted
        with transaction.atomic():
            new_title = project_creation_form.cleaned_data['project_title']
            new_strategy = project_creation_form.cleaned_data['search_strategy']
            project = save_project_from_form_or_raise_exception(new_title, new_strategy, request.user)

            forward_genome = request.FILES['forward_genome_file']
            backward_genome = request.FILES['backward_genome_file']
            query_sequences = request.FILES['query_sequence_file']

            save_genomes_and_query_in_db(query_sequences, forward_genome.name, backward_genome.name, project)
            save_forward_settings_from_form_or_raise_exception(project, settings_form_forward.cleaned_data)
            save_backward_settings_from_form_or_raise_exception(project, settings_form_backward.cleaned_data)

            create_project_dir(project)
            upload_file(forward_genome, 'media/' + 'databases/' + forward_genome.name)
            upload_file(backward_genome, 'media/' + 'databases/' + backward_genome.name)
            upload_file(query_sequences,
                        'media/' + str(project.id) + '/' + 'query_sequences' + '/' + query_sequences.name)

            write_snakefile(project.id)
    except Exception as e:
        raise IntegrityError("[-] Couldn't perform project creation due to exception: {}".format(e))
