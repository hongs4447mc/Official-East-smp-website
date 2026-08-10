import { exec } from "child_process";
import { promisify } from "util";

const run = promisify(exec);


export async function GET(){

    try {


        const { stdout, stderr } = await run(
            "node tools/ProjectScanner.js",
            {
                cwd: process.cwd()
            }
        );


        return new Response(

            JSON.stringify({

                success:true,

                message:"Scan completed",

                output:
                stdout || stderr

            }),

            {
                status:200,

                headers:{
                    "Content-Type":
                    "application/json"
                }
            }

        );


    }

    catch(error){


        return new Response(

            JSON.stringify({

                success:false,

                error:
                error.message

            }),

            {
                status:500,

                headers:{
                    "Content-Type":
                    "application/json"
                }
            }

        );


    }

}