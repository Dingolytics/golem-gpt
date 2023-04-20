Actions available:

human_input(query)
-> get input, review

read_file(filename)
-> read results, review

write_file(filename, content)
-> write results, review

http_request(url, method, headers, body, to_filename)
-> fetch results, write results, review

create_python_script(name, description, in_files, out_files)
-> delegate, write script, run script, review

create_shell_script(name, description, in_files, out_files)
-> delegate, write script, run script, review

run_script(name)
-> get results, review

ask_google(query, to_filename)
-> fetch results, review

delegate_job(goal, role, in_files, out_files)
-> create job, run job, review

explain(description)
-> explanation for current state

reject_job()
-> exit on failure

finish_job()
-> exit on success
