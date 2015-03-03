public class Aluno{

	private String nome;
	private String curso;
	private int nmec;

	Aluno(String nome, String curso){
		this.nome = nome;
		this.curso = curso;
	}
	Aluno(String nome){
		this.nome = nome;
	}

	public String getNome(){
		return this.nome;
	}

	public String getCurso(){
		return this.curso;
	}

	public int nmec(){
		return this.nmec;
	}

	static String universidade;

	static{
		universidade = "universidade de aveiro";
	}
	//private
	//protected
}


System.out.println(a.getNome());
System.out.println(a.getCurso());
